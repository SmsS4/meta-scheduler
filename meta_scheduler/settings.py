import dynaconf

all_settings = dynaconf.Dynaconf(
    settings_files=["settings.yaml", ".secrets.yaml"],
    environments=True,
    lowercase_read=False,
    load_dotenv=True,
    auto_cast=True,
)

db = all_settings.DB

# TODO better validators
all_settings.validators.register(
    ####### DB #######
    dynaconf.Validator(
        "DB.USER",
        "DB.DATABASE",
        "DB.PASSWORD",
        "DB.HOST",
        required=True,
        is_type_of=str,
    ),
    dynaconf.Validator(
        "DB.PORT",
        required=True,
        is_type_of=int,
        gt=0,
        lte=65535,
    ),
)

all_settings.validators.validate_all()
