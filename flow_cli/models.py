"""
Image model configuration.
"""

IMAGE_MODELS = {
    "gemini-2.5-flash-image-landscape": {
        "model_name": "GEM_PIX",
        "aspect_ratio": "IMAGE_ASPECT_RATIO_LANDSCAPE",
        "description": "Gemini 2.5 Flash - landscape",
    },
    "gemini-2.5-flash-image-portrait": {
        "model_name": "GEM_PIX",
        "aspect_ratio": "IMAGE_ASPECT_RATIO_PORTRAIT",
        "description": "Gemini 2.5 Flash - portrait",
    },
    "gemini-3.0-pro-image-landscape": {
        "model_name": "GEM_PIX_2",
        "aspect_ratio": "IMAGE_ASPECT_RATIO_LANDSCAPE",
        "description": "Gemini 3.0 Pro - landscape",
    },
    "gemini-3.0-pro-image-portrait": {
        "model_name": "GEM_PIX_2",
        "aspect_ratio": "IMAGE_ASPECT_RATIO_PORTRAIT",
        "description": "Gemini 3.0 Pro - portrait",
    },
    "gemini-3.0-pro-image-square": {
        "model_name": "GEM_PIX_2",
        "aspect_ratio": "IMAGE_ASPECT_RATIO_SQUARE",
        "description": "Gemini 3.0 Pro - square",
    },
    "gemini-3.0-pro-image-four-three": {
        "model_name": "GEM_PIX_2",
        "aspect_ratio": "IMAGE_ASPECT_RATIO_LANDSCAPE_FOUR_THREE",
        "description": "Gemini 3.0 Pro - 4:3 landscape",
    },
    "gemini-3.0-pro-image-three-four": {
        "model_name": "GEM_PIX_2",
        "aspect_ratio": "IMAGE_ASPECT_RATIO_PORTRAIT_THREE_FOUR",
        "description": "Gemini 3.0 Pro - 3:4 portrait",
    },
    "imagen-4.0-generate-preview-landscape": {
        "model_name": "IMAGEN_3_5",
        "aspect_ratio": "IMAGE_ASPECT_RATIO_LANDSCAPE",
        "description": "Imagen 4.0 - landscape",
    },
    "imagen-4.0-generate-preview-portrait": {
        "model_name": "IMAGEN_3_5",
        "aspect_ratio": "IMAGE_ASPECT_RATIO_PORTRAIT",
        "description": "Imagen 4.0 - portrait",
    },
    "gemini-3.1-flash-image-landscape": {
        "model_name": "NARWHAL",
        "aspect_ratio": "IMAGE_ASPECT_RATIO_LANDSCAPE",
        "description": "Gemini 3.1 Flash - landscape",
    },
    "gemini-3.1-flash-image-portrait": {
        "model_name": "NARWHAL",
        "aspect_ratio": "IMAGE_ASPECT_RATIO_PORTRAIT",
        "description": "Gemini 3.1 Flash - portrait",
    },
    "gemini-3.1-flash-image-square": {
        "model_name": "NARWHAL",
        "aspect_ratio": "IMAGE_ASPECT_RATIO_SQUARE",
        "description": "Gemini 3.1 Flash - square",
    },
    "gemini-3.1-flash-image-four-three": {
        "model_name": "NARWHAL",
        "aspect_ratio": "IMAGE_ASPECT_RATIO_LANDSCAPE_FOUR_THREE",
        "description": "Gemini 3.1 Flash - 4:3 landscape",
    },
    "gemini-3.1-flash-image-three-four": {
        "model_name": "NARWHAL",
        "aspect_ratio": "IMAGE_ASPECT_RATIO_PORTRAIT_THREE_FOUR",
        "description": "Gemini 3.1 Flash - 3:4 portrait",
    },
    "nano-banana-2-landscape": {
        "model_name": "NARWHAL",
        "aspect_ratio": "IMAGE_ASPECT_RATIO_LANDSCAPE",
        "description": "Nano Banana 2 - landscape",
    },
    "nano-banana-2-portrait": {
        "model_name": "NARWHAL",
        "aspect_ratio": "IMAGE_ASPECT_RATIO_PORTRAIT",
        "description": "Nano Banana 2 - portrait",
    },
    "nano-banana-2-square": {
        "model_name": "NARWHAL",
        "aspect_ratio": "IMAGE_ASPECT_RATIO_SQUARE",
        "description": "Nano Banana 2 - square",
    },
    "nano-banana-2-ultrawide": {
        "model_name": "NARWHAL",
        "aspect_ratio": "IMAGE_ASPECT_RATIO_LANDSCAPE",
        "description": "Nano Banana 2 - 21:9 ultrawide",
    },
    "nano-banana-pro-landscape": {
        "model_name": "GEM_PIX_2",
        "aspect_ratio": "IMAGE_ASPECT_RATIO_LANDSCAPE",
        "description": "Nano Banana Pro - landscape",
    },
    "nano-banana-pro-portrait": {
        "model_name": "GEM_PIX_2",
        "aspect_ratio": "IMAGE_ASPECT_RATIO_PORTRAIT",
        "description": "Nano Banana Pro - portrait",
    },
    "nano-banana-pro-square": {
        "model_name": "GEM_PIX_2",
        "aspect_ratio": "IMAGE_ASPECT_RATIO_SQUARE",
        "description": "Nano Banana Pro - square",
    },
}

DEFAULT_MODEL = "gemini-3.1-flash-image-landscape"


def list_models():
    """Print all available models."""
    print("\nAvailable image generation models:")
    print("-" * 60)
    for model_id, config in IMAGE_MODELS.items():
        default_mark = " (default)" if model_id == DEFAULT_MODEL else ""
        print(f"  {model_id}{default_mark}")
        print(f"    - {config['description']}")
    print("-" * 60)


def get_model_config(model_id: str) -> dict:
    """Get model configuration."""
    if model_id not in IMAGE_MODELS:
        raise ValueError(f"Unknown model: {model_id}")
    return IMAGE_MODELS[model_id]
