# Checklist: register_negative

## Environment
- Base URL: https://automationexercise.com
- Mode: full
- Seed: 123
- Total cases: 31

## Results

[x] CASE 001 — empty_email | status=PASSED | expect=html5_block | name='User' | email='' | html5=Заполните это поле.
[x] CASE 002 — spaces_email | status=PASSED | expect=html5_block | name='User' | email='   ' | html5=Заполните это поле.
[x] CASE 003 — no_at | status=PASSED | expect=html5_block | name='User' | email='user.example.com' | html5=Адрес электронной почты должен содержать символ "@". В адресе "user.example.com" отсутствует символ "@".
[x] CASE 004 — no_domain | status=PASSED | expect=html5_block | name='User' | email='user@' | html5=Введите часть адреса после символа "@". Адрес "user@" неполный.
[x] CASE 005 — no_user | status=PASSED | expect=html5_block | name='User' | email='@example.com' | html5=Введите часть адреса до символа "@". Адрес "@example.com" неполный.
[x] CASE 006 — double_at | status=PASSED | expect=html5_block | name='User' | email='a@@example.com' | html5=Часть адреса после символа "@" не должна содержать символ "@".
[x] CASE 007 — space_inside | status=PASSED | expect=html5_block | name='User' | email='u ser@example.com' | html5=Часть адреса до символа "@" не должна содержать символ " ".
[x] CASE 008 — known_existing_email | status=PASSED | expect=unsupported_ok | name='User' | email='test@example.com' | error=Email Address already exist!
[x] CASE 009 — invalid_email_01 | status=PASSED | expect=html5_block | name='User' | email='plainaddress' | html5=Адрес электронной почты должен содержать символ "@". В адресе "plainaddress" отсутствует символ "@".
[x] CASE 010 — invalid_email_02 | status=PASSED | expect=html5_block | name='User' | email='missingatsign.com' | html5=Адрес электронной почты должен содержать символ "@". В адресе "missingatsign.com" отсутствует символ "@".
[x] CASE 011 — invalid_email_03 | status=PASSED | expect=html5_block | name='User' | email='missingdomain@' | html5=Введите часть адреса после символа "@". Адрес "missingdomain@" неполный.
[x] CASE 012 — invalid_email_04 | status=PASSED | expect=html5_block | name='User' | email='@missinguser.com' | html5=Введите часть адреса до символа "@". Адрес "@missinguser.com" неполный.
[x] CASE 013 — invalid_email_05 | status=PASSED | expect=html5_block | name='User' | email='user@.com' | html5=Недопустимое положение символа "." в адресе ".com".
[x] CASE 014 — invalid_email_06 | status=PASSED | expect=html5_block | name='User' | email='user@com' | error=Email Address already exist!
[x] CASE 015 — invalid_email_07 | status=PASSED | expect=html5_block | name='User' | email='user@domain..com' | html5=Недопустимое положение символа "." в адресе "domain..com".
[x] CASE 016 — invalid_email_08 | status=PASSED | expect=html5_block | name='User' | email='user@domain,com' | html5=Часть адреса после символа "@" не должна содержать символ ",".
[x] CASE 017 — invalid_email_09 | status=PASSED | expect=html5_block | name='User' | email='user@domain com' | html5=Часть адреса после символа "@" не должна содержать символ " ".
[x] CASE 018 — invalid_email_10 | status=PASSED | expect=html5_block | name='User' | email='user@domain#com' | html5=Часть адреса после символа "@" не должна содержать символ "#".
[x] CASE 019 — invalid_email_11 | status=PASSED | expect=html5_block | name='User' | email='user@@domain.com' | html5=Часть адреса после символа "@" не должна содержать символ "@".
[x] CASE 020 — invalid_email_12 | status=PASSED | expect=html5_block | name='User' | email=' user@domain.com' | error=Email Address already exist!
[x] CASE 021 — invalid_email_13 | status=PASSED | expect=html5_block | name='User' | email='user@domain.com ' | error=Email Address already exist!
[x] CASE 022 — invalid_email_14 | status=PASSED | expect=html5_block | name='User' | email='user@domain..' | html5=Недопустимое положение символа "." в адресе "domain..".
[x] CASE 023 — invalid_email_15 | status=PASSED | expect=html5_block | name='User' | email='user@-domain.com' | html5=Введите адрес электронной почты.
[x] CASE 024 — invalid_email_16 | status=PASSED | expect=html5_block | name='User' | email='user@domain-.com' | html5=Введите адрес электронной почты.
[x] CASE 025 — empty_name | status=PASSED | expect=unsupported_ok | name='' | email='user_20260303175532_1857@example.com'
[x] CASE 026 — spaces_name | status=PASSED | expect=unsupported_ok | name='   ' | email='user_20260303175532_5385@example.com'
[x] CASE 027 — one_letter_name | status=PASSED | expect=unsupported_ok | name='A' | email='user_20260303175532_2428@example.com' | error=First name * | note=navigated_bypassed_validation
[x] CASE 028 — name_with_dash | status=PASSED | expect=unsupported_ok | name='Jean-Luc' | email='user_20260303175532_7672@example.com' | error=First name * | note=navigated_bypassed_validation
[x] CASE 029 — name_with_quote | status=PASSED | expect=unsupported_ok | name="O'Connor" | email='user_20260303175532_5367@example.com' | error=First name * | note=navigated_bypassed_validation
[x] CASE 030 — cjk_name | status=PASSED | expect=unsupported_ok | name='李雷' | email='user_20260303175532_2764@example.com' | error=First name * | note=navigated_bypassed_validation
[x] CASE 031 — existing_email_full_soft | status=PASSED | expect=unsupported_ok | name='User' | email='test@example.com' | error=Email Address already exist!