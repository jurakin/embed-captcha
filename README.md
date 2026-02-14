# Embed Captcha

A small library that displays a captcha challenge and returns a captcha response token.

> [!IMPORTANT]
> This library does not solve captcha - user action is required to obtain the token.

# Supported captchas

| Captcha                    | Support |
| -------------------------- | ------- |
| `CaptchaType.RECAPTCHA_V2` | ✅      |
| `CaptchaType.ReCaptcha V3` | ⏸️      |
| `CaptchaType.HCaptcha`     | ✅      |

# Example

`with` statement:

```python
from embed_captcha import Captcha, CaptchaType

with Captcha(
    "6LfD3PIbAAAAAJs_eEHvoOl75_83eXSqpPSRFJ_u",
    "https://2captcha.com/demo/recaptcha-v2",
    CaptchaType.RECAPTCHA_V2
) as captcha:
    print(captcha.token())
```

`.convert` function:

```python
from embed_captcha import Captcha, CaptchaType

captcha = Captcha()

# change arguments
captcha.convert(
    site_key="b17bafa7-90bf-4070-9296-626796423086",
    host="https://shimuldn.github.io/hcaptcha/",
    captcha_type=CaptchaType.HCAPTCHA
)
print(captcha.token())

# close window and cleanup
captcha.close()
```

Custom arguments:

```python
from embed_captcha import Captcha, CaptchaType, Window

# default profile
my_custom_profile: QWebEngineProfile = Window.temporary_profile(
    # default user agent
    user_agent = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/125.0.0.0 Safari/537.36 115Browser/35.13.0.2 Chromium/125.0"
)

captcha = Captcha(title="Fancy title", profile=my_custom_profile)
```

# Disclaimer

This project is intended for educational purposes only. The developers assume no liability and are not responsible for any misuse or damage caused by this program.
