from bioscout_tech_challenge.models.bounding_box import BoundingBox


def test_bounding_box_init():
    box = BoundingBox(x=1, y=1, width=2, height=3)
    assert box.x == 1
    assert box.y == 1
    assert box.width == 2
    assert box.height == 3
