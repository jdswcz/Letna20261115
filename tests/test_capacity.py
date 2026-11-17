"""Capacity-specific invariants, independent geometry fixture and invalid-input checks."""
import unittest
from decimal import Decimal

from shapely.geometry import Polygon
from tools.capacity import capacity, check_disjoint, shoelace, world_scale


class CapacityTests(unittest.TestCase):
    def test_known_triangle_and_translation(self):
        points = [(0,0),(10,0),(0,6)]
        self.assertEqual(shoelace(points), Decimal(30))
        self.assertEqual(shoelace([(x+458000,y+5550000) for x,y in reversed(points)]),Decimal(30))

    def test_half_pixel_world_file_is_required(self):
        meta = {"export":{"width":100,"height":50,"extent":{"xmin":0,"xmax":200,"ymin":0,"ymax":100}}}
        self.assertEqual(world_scale(meta,[2,0,0,-2,1,99]),(2,2))
        with self.assertRaises(ValueError):world_scale(meta,[2,0,0,-2,0,100])

    def test_adjacent_allowed_overlap_rejected(self):
        p=Polygon([(0,0),(10,0),(10,10),(0,10)])
        q=Polygon([(10,0),(20,0),(20,10),(10,10)])
        check_disjoint([p,q])
        with self.assertRaises(ValueError):check_disjoint([p,Polygon([(9,0),(20,0),(20,10),(9,10)])])

    def test_capacity_with_fixed_and_fractional_exclusions(self):
        self.assertEqual(capacity(100,3,.2,10),216)
        self.assertEqual(capacity(10.9,1),10)
        self.assertEqual(capacity(100,3,1),0)

    def test_reject_invalid_capacity_inputs(self):
        for args in [(100,-1),(100,2,1.1),(100,2,0,101),(float("nan"),2),(100,float("inf"))]:
            with self.subTest(args=args),self.assertRaises(ValueError):capacity(*args)


if __name__=="__main__":unittest.main()
