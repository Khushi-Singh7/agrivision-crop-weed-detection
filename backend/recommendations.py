
CROP_GUIDANCE = {
    "Wheat": {
        "prevention": [
            "Use clean seed and well-prepared fields.",
            "Inspect early growth for weed competition.",
            "Remove weeds before they set seed where practical."
        ],
        "management": [
            "Consider timely mechanical or manual weed removal.",
            "Identify the weed species before choosing a control method.",
            "Follow locally recommended integrated weed management practices."
        ]
    },
    "Rice": {
        "prevention": [
            "Use clean seed and monitor fields early.",
            "Manage irrigation and water levels according to the rice system.",
            "Inspect field margins and remove weeds before seed production."
        ],
        "management": [
            "Choose control methods suitable for transplanted or direct-seeded rice.",
            "Use mechanical or manual removal where practical.",
            "Confirm weed species and crop stage before selecting any herbicide."
        ]
    },
    "Sugarcane": {
        "prevention": [
            "Maintain clean planting material and field margins.",
            "Monitor weeds during early crop establishment.",
            "Use suitable intercultural practices to reduce weed competition."
        ],
        "management": [
            "Consider inter-row cultivation where safe for the crop.",
            "Use suitable mulch practices where appropriate.",
            "Confirm crop stage and weed species before chemical treatment."
        ]
    },
    "Maize": {
        "prevention": [
            "Use clean seed and monitor fields from early emergence.",
            "Control weeds before they establish or produce seed.",
            "Use crop-appropriate spacing and agronomic practices."
        ],
        "management": [
            "Consider timely mechanical or manual weed control.",
            "Avoid damaging maize roots during cultivation.",
            "Check the product label and crop stage before chemical treatment."
        ]
    },
    "Cotton": {
        "prevention": [
            "Inspect fields regularly, especially during early growth.",
            "Keep field margins and irrigation channels monitored.",
            "Prevent weeds from producing and spreading seed."
        ],
        "management": [
            "Consider mechanical or manual control where suitable.",
            "Avoid damaging cotton plants during inter-row cultivation.",
            "Verify crop safety and local label directions before treatment."
        ]
    },
    "Vegetables": {
        "prevention": [
            "Inspect beds and growing areas frequently.",
            "Use clean planting material and suitable mulch where appropriate.",
            "Remove weeds early before they compete with young plants."
        ],
        "management": [
            "Hand removal or shallow cultivation may be suitable for some crops.",
            "Protect shallow vegetable roots while removing weeds.",
            "Verify the exact vegetable crop and product label before chemical use."
        ]
    }
}


def get_recommendations(crop, weed_count):
    guidance = CROP_GUIDANCE[crop]

    if weed_count > 0:
        status = (
            f"The model detected {weed_count} object(s) labelled "
            "'weed'. The species has not been identified."
        )
        management = guidance["management"]
    else:
        status = (
            "No weeds were detected above the current confidence "
            "threshold. This does not prove that the field is weed-free."
        )
        management = [
            "Continue routine field scouting.",
            "Review the image and consider lowering the threshold "
            "if weeds may have been missed.",
            "Inspect the field directly before making management decisions."
        ]

    return {
        "status": status,
        "prevention": guidance["prevention"],
        "management": management,
        "safety": (
            "These are general management suggestions, not a diagnosis "
            "or a pesticide prescription. Identify the weed and confirm "
            "the crop, growth stage, location and locally approved label "
            "before using a chemical treatment."
        )
    }
