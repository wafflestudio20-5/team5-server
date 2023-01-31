import pytest


# upload one
@pytest.mark.django_db
def test_post_image(login_adminclient, productinfo, temporary_images):
    r = login_adminclient.post(f'/shop/productinfos/{productinfo[0].id}/images/',
                               {'product_image': temporary_images[0]})
    assert r.status_code == 201
    r = login_adminclient.get(f'/shop/productinfos/{productinfo[0].id}/images/')
    assert r.status_code == 200


# upload several
@pytest.mark.django_db
def test_post_images(login_adminclient, productinfo, temporary_images):
    r = login_adminclient.post(f'/shop/productinfos/{productinfo[0].id}/images/',
                               {'product_image': temporary_images})
    assert r.status_code == 201
    r = login_adminclient.get(f'/shop/productinfos/{productinfo[0].id}/images/')
    assert r.status_code == 200
