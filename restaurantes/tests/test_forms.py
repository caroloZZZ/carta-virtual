import pytest
from restaurantes.forms import RegistroUsuarioForm, RegistroRestauranteForm


@pytest.mark.django_db
class TestRegistroUsuarioForm:
    def test_form_valido(self):
        data = {
            "username": "testuser",
            "email": "test@example.com",
            "password1": "Compleja123!",
            "password2": "Compleja123!",
        }
        form = RegistroUsuarioForm(data)
        assert form.is_valid()

    def test_password_no_coinciden(self):
        data = {
            "username": "testuser",
            "email": "test@example.com",
            "password1": "pass123",
            "password2": "pass456",
        }
        form = RegistroUsuarioForm(data)
        assert not form.is_valid()
        assert "password2" in form.errors


@pytest.mark.django_db
class TestRegistroRestauranteForm:
    def test_form_valido(self):
        data = {
            "nombre": "Restaurante Test",
            "tipo": "restaurante",
            "descripcion": "Descripción",
            "direccion": "Calle 123",
            "telefono": "12345678",
            "email": "test@rest.com",
        }
        form = RegistroRestauranteForm(data)
        assert form.is_valid()

    def test_telefono_invalido(self):
        data = {
            "nombre": "Restaurante Test",
            "tipo": "restaurante",
            "descripcion": "Descripción",
            "direccion": "Calle 123",
            "telefono": "ABC123",
            "email": "test@rest.com",
        }
        form = RegistroRestauranteForm(data)
        assert not form.is_valid()
