import pytest
from django.urls import reverse
from accounts.models import CustomUser


@pytest.mark.django_db
def test_verification_login(rf, client, test_user_info, mailoutbox):
    email, password, shoe_size = test_user_info
    r = client.post('/accounts/registration/', data={"email": email, "password1":password, "password2":password, "shoe_size":shoe_size})
    assert r.status_code == 201
    assert len(mailoutbox) == 1
    activation_key = mailoutbox[0].body.split('http://')[1].split('4')
    r = client.post('/accounts/registration/verify-email/', {"key": activation_key})
    assert r.status_code, 200




