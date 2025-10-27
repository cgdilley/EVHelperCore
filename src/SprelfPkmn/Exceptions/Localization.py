
class LocalizationError(Exception):

    @staticmethod
    def for_lang(lang: str):
        return LocalizationError(f"Unsupported language '{lang}'.")
