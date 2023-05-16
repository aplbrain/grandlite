# Output and error types for the prompt:
_Output = _Error = str | None
# The response type for the prompt (railroad-style tuple)
Response = tuple[_Output, _Error]
