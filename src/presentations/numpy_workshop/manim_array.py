"""Utility datatypes to represent numpy arrays in manim."""

from typing import Self

import numpy as np
from manim import constants
from manim.mobject.geometry import polygram
from manim.mobject.text import text_mobject
from manim.mobject.types import vectorized_mobject

_MAX_CELL_CONTENT_FILL = 0.8


class Cell(vectorized_mobject.VMobject):
    """Representation of a single array element."""

    def __init__(self, description: str) -> None:
        super().__init__()
        cell = polygram.Square()
        content = text_mobject.Text(text=description)
        if content.width > cell.width * _MAX_CELL_CONTENT_FILL:
            content = content.scale_to_fit_width(cell.width * _MAX_CELL_CONTENT_FILL)
        self.add(cell)
        self.add(content)
        content.move_to(cell.get_center())


class ManimArray(vectorized_mobject.VGroup):
    """Representation of a numpy array."""

    def __init__(self, array: np.ndarray, **kwargs) -> None:
        super().__init__(**kwargs)
        self._array = array

        self.add(self._build_array(self._array))
        self.arrange_array_()

    @staticmethod
    def _build_array(array: np.ndarray) -> vectorized_mobject.VGroup:
        """Build array structure using nested VGroups."""

        def _build_subarray(array: np.ndarray) -> vectorized_mobject.VGroup:
            if array.ndim > 1:
                array_group = vectorized_mobject.VGroup()
                for subarray in array:
                    array_group.add(_build_subarray(subarray))
                return array_group
            return vectorized_mobject.VGroup(*(Cell(str(value)) for value in array))

        return _build_subarray(array)

    def arrange_array_(
        self,
        buff: float = constants.DEFAULT_MOBJECT_TO_MOBJECT_BUFFER,
        center: bool = True,
        **kwargs,
    ) -> Self:
        """
        Arrange elements according to the shape of the array in two dimensions.

        To represent n-dimensional arrays within two dimensions, dimensions are
        alternating between using horizontal and vertical space - increasing the
        spacing between neighbouring elements with increasing dimensionality.


        Parameters
        ----------
        buff
            Buffer space between elements of the first dimension.
        center
            Flag to center elements when arranging.
        kwargs
            Additional keyword arguments passed to arrange.

        Returns
        -------
        Self
            The ManimArray.
        """

        def _arrange_subarray_(
            matrix_objects: vectorized_mobject.VGroup | Cell,
            buff: float,
            center: bool,
            **kwargs,
        ) -> int:
            if isinstance(matrix_objects, Cell):
                return -1
            dimension = 0
            for submatrix_objects in matrix_objects:
                dimension = _arrange_subarray_(
                    submatrix_objects, buff, center, **kwargs
                )
            direction = constants.DOWN if dimension % 2 == 0 else constants.RIGHT
            buffer = buff * 2 ** ((dimension - 1) // 2)
            matrix_objects.arrange(direction, buffer, center, **kwargs)
            return dimension + 1

        _arrange_subarray_(
            self.submobjects[0],
            buff=buff,
            center=center,
            **kwargs,
        )
        return self
