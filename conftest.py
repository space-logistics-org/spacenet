from hypothesis import settings, Verbosity

settings.register_profile("slow", settings(max_examples=1000))
settings.register_profile("dev", settings(max_examples=50, derandomize=True))
settings.register_profile(
    "debug", settings(max_examples=50, derandomize=True, verbosity=Verbosity.verbose)
)
