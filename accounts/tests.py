from django.core import mail
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase



class AccountTests(APITestCase):
    register_url = reverse('rest_register')
    verify_email_url = reverse('rest_verify_email')
    login_url = reverse('login')
    logout_url = reverse('rest_logout')

    # @classmethod
    # def setUpClass(cls):
    #     super().setUpClass()
    #
    def setUp(self):
        self.default_data = {
            'email': 'loveyoony20@naver.com',
            'password': 'luce1013!'
        }


    def test_create_account_and_login(self):
        data = {
            'email': 'test@example.com',
            'password1': 'testpass@!',
            'password2': 'testpass@!',
            'shoe_size': '255',
        }
        response = self.client.post(self.register_url, data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.json()["detail"], "확인 이메일을 발송했습니다.")

        login_data = {
            'email': 'test@example.com',
            'password': 'testpass@!'
        }

        #try to login without email verification
        response = self.client.post(self.login_url, login_data)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertTrue(
            '이메일 주소가 확인되지 않았습니다.' in response.json()["non_field_errors"]
        )

        #get the key from verification email
        self.assertEqual(len(mail.outbox), 1)
        email_lines = mail.outbox[0].body.splitlines()
        activation_line = [i for i in email_lines if "account-confirm-email" in i][0]
        activation_link = activation_line.split("에서")[0]
        activation_key = activation_link.split("/")[6]

        # Verify
        response = self.client.post(self.verify_email_url, {"key": activation_key})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.json()["detail"], "ok")

        #incorrect info login
        response = self.client.post(self.login_url, {
            'email': 'testwrong@example.com',
            'password':'testpass@!'
        })
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertTrue("Unable to log in with provided credentials." in response.json()["non_field_errors"])

        #correct info login
        response = self.client.post(self.login_url, login_data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertTrue("access_token" in response.json())

    def test_unauthorized_logout(self):
        response = self.client.post(self.logout_url, {})
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
        self.assertTrue(
            "Refresh token was not included in request data." in response.json()["detail"]
        )



