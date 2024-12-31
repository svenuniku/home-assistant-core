from dataclasses import dataclass

from homeassistant.components.sensor import SensorEntityDescription

from .const import (
    TYPE_WASTE_BULKY_GOODS,
    TYPE_WASTE_CARDBOARD,
    TYPE_WASTE_CARGOTRAM,
    TYPE_WASTE_CHIPPING,
    TYPE_WASTE_ETRAM,
    TYPE_WASTE_INCOMBUSTIBLE,
    TYPE_WASTE_METAL,
    TYPE_WASTE_OEKIBUS,
    TYPE_WASTE_ORGANIC,
    TYPE_WASTE_PAPER,
    TYPE_WASTE_SPECIAL,
    TYPE_WASTE_TEXTILE,
    TYPE_WASTE_WASTE,
)


@dataclass(frozen=True, kw_only=True)
class OpenERZSensorEntityDescription(SensorEntityDescription):
    """Define a class that describes OpenUV sensor entities."""

    has_entity_name = True
    # value_fn: Callable[[dict[str, Any]], int | str]


SENSOR_DESCRIPTIONS: dict[str, OpenERZSensorEntityDescription] = {
    TYPE_WASTE_BULKY_GOODS: OpenERZSensorEntityDescription(
        key=TYPE_WASTE_BULKY_GOODS,
        translation_key="bulky_goods",
        # value_fn=lambda data: data["ozone"],
    ),
    TYPE_WASTE_CARDBOARD: OpenERZSensorEntityDescription(
        key=TYPE_WASTE_CARDBOARD,
        translation_key="cardboard",
    ),
    TYPE_WASTE_CARGOTRAM: OpenERZSensorEntityDescription(
        key=TYPE_WASTE_CARGOTRAM,
        translation_key="cargotram",
    ),
    TYPE_WASTE_CHIPPING: OpenERZSensorEntityDescription(
        key=TYPE_WASTE_CHIPPING,
        translation_key="chipping_service",
    ),
    TYPE_WASTE_ETRAM: OpenERZSensorEntityDescription(
        key=TYPE_WASTE_ETRAM,
        translation_key="etram",
    ),
    TYPE_WASTE_INCOMBUSTIBLE: OpenERZSensorEntityDescription(
        key=TYPE_WASTE_INCOMBUSTIBLE,
        translation_key="incombustibles",
    ),
    TYPE_WASTE_METAL: OpenERZSensorEntityDescription(
        key=TYPE_WASTE_METAL,
        translation_key="metal",
    ),
    TYPE_WASTE_OEKIBUS: OpenERZSensorEntityDescription(
        key=TYPE_WASTE_OEKIBUS,
        translation_key="oekibus",
    ),
    TYPE_WASTE_ORGANIC: OpenERZSensorEntityDescription(
        key=TYPE_WASTE_ORGANIC,
        translation_key="organic",
    ),
    TYPE_WASTE_PAPER: OpenERZSensorEntityDescription(
        key=TYPE_WASTE_PAPER,
        translation_key="paper",
    ),
    TYPE_WASTE_SPECIAL: OpenERZSensorEntityDescription(
        key=TYPE_WASTE_SPECIAL,
        translation_key="special",
    ),
    TYPE_WASTE_TEXTILE: OpenERZSensorEntityDescription(
        key=TYPE_WASTE_TEXTILE,
        translation_key="textile",
    ),
    TYPE_WASTE_WASTE: OpenERZSensorEntityDescription(
        key=TYPE_WASTE_WASTE,
        translation_key="waste",
    ),
}
