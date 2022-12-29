from django.core import mail
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase


class AccountTests(APITestCase):
    register_url = reverse('rest_register')
    verify_email_url = reverse('rest_verify_email')
    login_url = reverse('login')

    def test_create_account_and_login(self):
        data = {
            'email': 'test@example.com',
            'password1': 'testpass@!',
            'password2': 'testpass@!',
            'shoe_size': '255',
        }

        response = self.client.post(self.register_url, data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.json()["detail"], "Verification e-mail sent.")

        login_data = {
            'email': 'test@example.com',
            'password': 'testpass@!'
        }
        response = self.client.post(self.login_url, login_data)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertTrue(
            "E-mail is not verified." in response.json()["non_field_errors"]
        )

        self.assertEqual(len(mail.outbox), 1)
        email_lines = mail.outbox[0].body.splitlines()
        activation_line = [i for i in email_lines if "account-confirm-email" in i][0]
        activation_link = activation_line.split("go to ")[1]
        activation_key = activation_link.split("/")[7]

        # Verify
        response = self.client.post(self.verify_email_url, {"key": activation_key})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.json()["detail"], "ok")

        response = self.client.post(self.login_url, login_data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertTrue("access_token" in response.json())
