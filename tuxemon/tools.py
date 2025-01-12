#
# Tuxemon
# Copyright (C) 2014, William Edwards <shadowapex@gmail.com>,
#                     Benjamin Bean <superman2k5@gmail.com>
#
# This file is part of Tuxemon.
#
# Tuxemon is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# Tuxemon is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with Tuxemon.  If not, see <http://www.gnu.org/licenses/>.
#
# Contributor(s):
#
# William Edwards <shadowapex@gmail.com>
# Derek Clark <derekjohn.clark@gmail.com>
# Leif Theden <leif.theden@gmail.com>
#
#
from __future__ import annotations
from typing import (Any, Optional, Protocol, Sequence, Tuple, Type, TypeVar,
    Union, Mapping, Iterable, TYPE_CHECKING, Callable)
import typing
from tuxemon.math import Vector2

"""

Do not import platform-specific libraries such as pygame.
Graphics/audio operations should go to their own modules.

As the game library is developed and matures, move these into larger modules
if more appropriate.  Ideally this should be kept small.

"""

import logging
import re
from itertools import zip_longest

from tuxemon.compat import ReadOnlyRect
from tuxemon import prepare
from tuxemon.locale import T

if TYPE_CHECKING:
    from tuxemon.session import Session
    from tuxemon.sprite import Sprite
    from tuxemon.item.item import Item
    from tuxemon.state import State
    import pygame

logger = logging.getLogger(__name__)

TVar = TypeVar("TVar")
TVarSequence = TypeVar("TVarSequence", bound=Tuple[int, ...])

ValidParameterSingleType = Optional[Type[Any]]
ValidParameterTypes = Union[
    ValidParameterSingleType,
    Sequence[ValidParameterSingleType],
]


class NamedTupleProtocol(Protocol):
    """Protocol for arbitrary NamedTuple objects."""

    @property
    def _fields(self) -> Tuple[str, ...]:
        pass


NamedTupleTypeVar = TypeVar("NamedTupleTypeVar", bound=NamedTupleProtocol)


def get_cell_coordinates(
    rect: ReadOnlyRect,
    point: Tuple[int, int],
    size: Tuple[int, int],
) -> Tuple[int, int]:
    """Find the cell of size, within rect, that point occupies."""
    point = (point[0] - rect.x, point[1] - rect.y)
    cell_x = (point[0] // size[0]) * size[0]
    cell_y = (point[1] // size[1]) * size[1]
    return (cell_x, cell_y)


def transform_resource_filename(*filename: str) -> str:
    """
    Appends the resource folder name to a filename.

    Parameters:
        filename: Relative path of a resource.

    Returns:
        The absolute path of the resource.

    """
    return prepare.fetch(*filename)


def scale_sequence(sequence: TVarSequence) -> TVarSequence:
    """
    Scale a sequence of integers by the configured scale factor.

    Parameters:
        sequence: Sequence to scale.

    Returns:
        Scaled sequence.

    """
    return type(sequence)(i * prepare.SCALE for i in sequence)


def scale(number: int) -> int:
    """
    Scale an integer by the configured scale factor.

    Parameter:
        number: Integer to scale.

    Returns:
        Scaled integer.

    """
    return prepare.SCALE * number


def calc_dialog_rect(screen_rect: pygame.rect.Rect) -> pygame.rect.Rect:
    """
    Return a rect that is the area for a dialog box on the screen.

    Note:
        This only works with Pygame rects, as it modifies the attributes.

    Parameters:
        screen_rect: Rectangle of the screen.

    Returns:
        Rectangle for a dialog.

    """
    rect = screen_rect.copy()
    if prepare.CONFIG.large_gui:
        rect.height *= 4
        rect.height //= 10
        rect.bottomleft = screen_rect.bottomleft
    else:
        rect.height //= 4
        rect.width *= 8
        rect.width //= 10
        rect.center = screen_rect.centerx, screen_rect.bottom - rect.height
    return rect


def open_dialog(
    session: Session,
    text: Sequence[str],
    avatar: Optional[Sprite] = None,
    menu: Optional[Tuple[str, str, Callable[[], None]]] = None,
) -> State:
    """
    Open a dialog with the standard window size.

    Parameters:
        session: Game session.
        text: List of strings.
        avatar: Optional avatar sprite.
        menu: Optional menu object.

    Returns:
        The pushed dialog state.

    """
    rect = calc_dialog_rect(session.client.screen.get_rect())
    return session.client.push_state(
        "DialogState",
        text=text,
        avatar=avatar,
        rect=rect,
        menu=menu,
    )


def nearest(l: Iterable[float]) -> Sequence[int]:
    """
    Use rounding to find nearest tile."""
    return tuple(int(round(i)) for i in l)


def vector2_to_tile_pos(vector: Vector2) -> Tuple[int, int]:
    return (int(vector[0]), int(vector[1]))


def number_or_variable(
    session: Session,
    value: str,
) -> float:
    """
    Returns a numeric game variable by its name.

    If ``value`` is already a number, convert from string to float and
    return that.

    Parameters:
        session: Session object, that contains the requested variable.
        value: Name of the requested variable or string with numerical value.

    Returns:
        Numerical value contained in the string or in the variable referenced
        by that name.

    Raises:
        ValueError: If ``value`` is not a number but no numeric variable with
        that name can be retrieved.

    """
    player = session.player
    if value.isdigit():
        return float(value)
    else:
        try:
            return float(player.game_variables[value])
        except (KeyError, ValueError, TypeError):
            logger.error(f"invalid number or game variable {value}")
            raise ValueError


def cast_values(
    parameters: Sequence[Any],
    valid_parameters: Sequence[Tuple[ValidParameterTypes, str]],
) -> Sequence[Any]:
    """
    Change all the string values to the expected type.

    This will also check and enforce the correct parameters for actions.

    Parameters:
        parameters: Parameters passed to the scripted object.
        valid_parameters: Allowed parameters and their types.

    Returns:
        Parameters converted to their correct type.

    """

    # TODO: stability/testing
    def cast(
        i: Tuple[Tuple[ValidParameterTypes, str], Any],
    ) -> Any:
        ve = False
        t, v = i
        try:
            for tt in t[0]:
                if tt is None or tt is type(None):
                    return None

                if v is None:
                    return None

                try:
                    return tt(v)
                except ValueError:
                    ve = True

        except TypeError:
            if v is None:
                return None

            if v == "":
                return None

            return t[0](v)

        if ve:
            raise ValueError

    try:
        return list(map(cast, zip_longest(valid_parameters, parameters)))
    except ValueError:
        logger.error("Invalid parameters passed:")
        logger.error(f"expected: {valid_parameters}")
        logger.error(f"got: {parameters}")
        raise


def get_types_tuple(
    param_type: ValidParameterSingleType,
) -> Sequence[ValidParameterSingleType]:
    if typing.get_origin(param_type) is Union:
        return typing.get_args(param_type)
    else:
        return (param_type,)


def cast_parameters_to_namedtuple(
    parameters: Sequence[Any],
    namedtuple_class: Type[NamedTupleTypeVar],
) -> NamedTupleTypeVar:
    valid_parameters = [
        (get_types_tuple(typing.get_type_hints(namedtuple_class)[f]), f) for f in namedtuple_class._fields
    ]

    values = cast_values(parameters, valid_parameters)
    return namedtuple_class(*values)


def show_item_result_as_dialog(
    session: Session,
    item: Item,
    result: Mapping[str, Any],
) -> None:
    """
    Show generic dialog if item was used or not.

    Parameters:
        session: Game session.
        item: Item object.
        result: A dict with a ``success`` key indicating sucess or failure.

    """
    msg_type = "use_success" if result["success"] else "use_failure"
    template = getattr(item, msg_type)
    if template:
        message = T.translate(template)
        open_dialog(session, [message])


def split_escaped(string_to_split: str, delim: str = ",") -> Sequence[str]:
    """
    Splits a string by the specified deliminator excluding escaped ones.

    Parameters:
        string_to_split: The string to split.
        delim: The deliminator to split the string by.

    Returns:
        A list of the splitted string.

    """
    # Split by "," unless it is escaped by a "\"
    split_list = re.split(r"(?<!\\)" + delim, string_to_split)

    # Remove the escape character from the split list
    split_list = [w.replace(r"\,", ",") for w in split_list]

    # strip whitespace around each
    split_list = [i.strip() for i in split_list]

    return split_list


def round_to_divisible(x: float, base: int = 16) -> int:
    """
    Rounds a number to a divisible base.

    This is used to round collision areas that aren't defined well. This
    function assists in making sure collisions work if the map creator didn't
    set the collision areas to round numbers.

    Parameters:
        x: The number we want to round.
        base: The base that we want our number to be divisible by. By default
            this is 16.

    Returns:
        Rounded number that is divisible by ``base``.

    """
    return int(base * round(float(x) / base))


def copy_dict_with_keys(
    source: Mapping[str, TVar],
    keys: Iterable[str],
) -> Mapping[str, TVar]:
    """
    Return new dict using only the keys/value from ``keys``.

    If key from keys is not present no error is raised.

    Parameters:
        source: Original mapping.
        keys: Allowed keys in the output mapping.

    Returns:
        New mapping with the keys restricted to those in ``keys``.

    """
    return {k: source[k] for k in keys if k in source}
