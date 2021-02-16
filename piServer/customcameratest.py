import unittest
import customcamera
import time



"""
Tests the available valid options for each field
"""
class TestValidOptions(unittest.TestCase):
    def test_get_valid_options(self):
        self.assertEqual(customcamera.get_valid_debug(), [True, False])
        self.assertEqual(customcamera.get_valid_resolutions(), ["720p", "480p", "360p", "240p"])
        self.assertEqual(customcamera.get_valid_framerate(), [*range(5, 61, 5)])
        self.assertEqual(customcamera.get_valid_hflip(), [True, False])
        self.assertEqual(customcamera.get_valid_vflip(), [True, False])
        self.assertEqual(customcamera.get_valid_rotation(), [0, 90, 180, 270])
        self.assertEqual(customcamera.get_valid_iso(), [0, 100, 200, 320, 400, 500, 640, 800])
        self.assertEqual(customcamera.get_valid_brightness(), [*range(0, 101, 1)])
        self.assertEqual(customcamera.get_valid_contrast(), [*range(-100, 101, 1)])
        self.assertEqual(customcamera.get_valid_saturation(), [*range(-100, 101, 1)])
        self.assertEqual(customcamera.get_valid_stabilization(), [True, False])

"""
Tests the default option for each field
"""
class TestDefaults(unittest.TestCase):
    def test_defaults(self):
        self.assertEqual(customcamera.CameraDefaults.CAMERA_RESOLUTION_DEFAULT, "480p")
        self.assertEqual(customcamera.CameraDefaults.CAMERA_FRAMERATE_DEFAULT, 60)
        self.assertEqual(customcamera.CameraDefaults.CAMERA_HFLIP_DEFAULT, False)
        self.assertEqual(customcamera.CameraDefaults.CAMERA_VFLIP_DEFAULT, False)
        self.assertEqual(customcamera.CameraDefaults.CAMERA_ROTATION_DEFAULT, 0)
        self.assertEqual(customcamera.CameraDefaults.CAMERA_ISO_DEFAULT, 0)
        self.assertEqual(customcamera.CameraDefaults.CAMERA_BRIGHTNESS_DEFAULT, 50)
        self.assertEqual(customcamera.CameraDefaults.CAMERA_CONTRAST_DEFAULT, 0)
        self.assertEqual(customcamera.CameraDefaults.CAMERA_SATURATION_DEFAULT, 0)
        self.assertEqual(customcamera.CameraDefaults.CAMERA_STABILIZATION_DEFAULT, False)
        self.assertEqual(customcamera.CameraDefaults.OTHER_DEBUG, False)

"""
Tests that each field is populated correctly at start
"""
class TestCameraDefaultInitialization(unittest.TestCase):
    def test_initialization(self):
        with customcamera.CustomCamera({}) as testCam:
            self.assertEqual(testCam.get_debug(), customcamera.CameraDefaults.OTHER_DEBUG)
            self.assertEqual(testCam.get_resolution(), customcamera.CameraDefaults.CAMERA_RESOLUTION_DEFAULT)
            self.assertEqual(testCam.get_framerate(), customcamera.CameraDefaults.CAMERA_FRAMERATE_DEFAULT)
            self.assertEqual(testCam.get_hflip(), customcamera.CameraDefaults.CAMERA_HFLIP_DEFAULT)
            self.assertEqual(testCam.get_vflip(), customcamera.CameraDefaults.CAMERA_VFLIP_DEFAULT)
            self.assertEqual(testCam.get_rotation(), customcamera.CameraDefaults.CAMERA_ROTATION_DEFAULT)
            self.assertEqual(testCam.get_iso(), customcamera.CameraDefaults.CAMERA_ISO_DEFAULT)
            self.assertEqual(testCam.get_brightness(), customcamera.CameraDefaults.CAMERA_BRIGHTNESS_DEFAULT)
            self.assertEqual(testCam.get_contrast(), customcamera.CameraDefaults.CAMERA_CONTRAST_DEFAULT)
            self.assertEqual(testCam.get_saturation(), customcamera.CameraDefaults.CAMERA_SATURATION_DEFAULT)
            self.assertEqual(testCam.get_stabilization(), customcamera.CameraDefaults.CAMERA_STABILIZATION_DEFAULT)

"""
Tests that each option passed meets the criteria for default, valid and invalid parameters for debug
"""
class TestCameraInitializationDebug(unittest.TestCase):
    def test_initialization_default(self):
        passed_dict = dict([("debug", customcamera.CameraDefaults.OTHER_DEBUG)])
        with customcamera.CustomCamera(passed_dict) as testCam:
            self.assertEqual(testCam.get_debug(), passed_dict["debug"])

    def test_initialization_proper(self):
        passed_dict = dict([("debug", True)])
        with customcamera.CustomCamera(passed_dict) as testCam:
            self.assertEqual(testCam.get_debug(), passed_dict["debug"])

    def test_initialization_nonproper(self):
        passed_dict = dict([("debug", 5)])
        with customcamera.CustomCamera(passed_dict) as testCam:
            self.assertNotEqual(testCam.get_debug(), passed_dict["debug"])
            self.assertEqual(testCam.get_debug(), customcamera.CameraDefaults.OTHER_DEBUG)

"""
Tests that each option passed meets the criteria for default, valid and invalid parameters for Resolution
"""
class TestCameraInitializationResolution(unittest.TestCase):
    def test_initialization_default(self):
        passed_dict = dict([("resolution", customcamera.CameraDefaults.CAMERA_RESOLUTION_DEFAULT)])
        with customcamera.CustomCamera(passed_dict) as testCam:
            self.assertEqual(testCam.get_resolution(), passed_dict["resolution"])

    def test_initialization_proper(self):
        passed_dict = dict([("resolution", "720p")])
        with customcamera.CustomCamera(passed_dict) as testCam:
            self.assertEqual(testCam.get_resolution(), passed_dict["resolution"])

    def test_initialization_nonproper(self):
        passed_dict = dict([("resolution", 5)])
        with customcamera.CustomCamera(passed_dict) as testCam:
            self.assertNotEqual(testCam.get_resolution(), passed_dict["resolution"])
            self.assertEqual(testCam.get_resolution(), customcamera.CameraDefaults.CAMERA_RESOLUTION_DEFAULT)

"""
Tests that each option passed meets the criteria for default, valid and invalid parameters for Framerate
"""
class TestCameraInitializationFramerate(unittest.TestCase):
    def test_initialization_default(self):
        passed_dict = dict([("framerate", customcamera.CameraDefaults.CAMERA_FRAMERATE_DEFAULT)])
        with customcamera.CustomCamera(passed_dict) as testCam:
            self.assertEqual(testCam.get_framerate(), passed_dict["framerate"])

    def test_initialization_proper(self):
        passed_dict = dict([("framerate", 10)])
        with customcamera.CustomCamera(passed_dict) as testCam:
            self.assertEqual(testCam.get_framerate(), passed_dict["framerate"])

    def test_initialization_nonproper(self):
        passed_dict = dict([("framerate", 0)])
        with customcamera.CustomCamera(passed_dict) as testCam:
            self.assertNotEqual(testCam.get_framerate(), passed_dict["framerate"])
            self.assertEqual(testCam.get_framerate(), customcamera.CameraDefaults.CAMERA_FRAMERATE_DEFAULT)

"""
Tests that each option passed meets the criteria for default, valid and invalid parameters for H-FLIP
"""
class TestCameraInitializationHflip(unittest.TestCase):
    def test_initialization_default(self):
        passed_dict = dict([("hflip", customcamera.CameraDefaults.CAMERA_HFLIP_DEFAULT)])
        with customcamera.CustomCamera(passed_dict) as testCam:
            self.assertEqual(testCam.get_hflip(), passed_dict["hflip"])

    def test_initialization_proper(self):
        passed_dict = dict([("hflip", True)])
        with customcamera.CustomCamera(passed_dict) as testCam:
            self.assertEqual(testCam.get_hflip(), passed_dict["hflip"])

    def test_initialization_nonproper(self):
        passed_dict = dict([("hflip", 10)])
        with customcamera.CustomCamera(passed_dict) as testCam:
            self.assertNotEqual(testCam.get_hflip(), passed_dict["hflip"])
            self.assertEqual(testCam.get_hflip(), customcamera.CameraDefaults.CAMERA_HFLIP_DEFAULT)

"""
Tests that each option passed meets the criteria for default, valid and invalid parameters for V-FLIP
"""
class TestCameraInitializationVflip(unittest.TestCase):
    def test_initialization_default(self):
        passed_dict = dict([("vflip", customcamera.CameraDefaults.CAMERA_VFLIP_DEFAULT)])
        with customcamera.CustomCamera(passed_dict) as testCam:
            self.assertEqual(testCam.get_vflip(), passed_dict["vflip"])

    def test_initialization_proper(self):
        passed_dict = dict([("vflip", True)])
        with customcamera.CustomCamera(passed_dict) as testCam:
            self.assertEqual(testCam.get_vflip(), passed_dict["vflip"])

    def test_initialization_nonproper(self):
        passed_dict = dict([("vflip", 10)])
        with customcamera.CustomCamera(passed_dict) as testCam:
            self.assertNotEqual(testCam.get_vflip(), passed_dict["vflip"])
            self.assertEqual(testCam.get_vflip(), customcamera.CameraDefaults.CAMERA_VFLIP_DEFAULT)

"""
Tests that each option passed meets the criteria for default, valid and invalid parameters for Rotation
"""
class TestCameraInitializationRotation(unittest.TestCase):
    def test_initialization_default(self):
        passed_dict = dict([("rotation", customcamera.CameraDefaults.CAMERA_ROTATION_DEFAULT)])
        with customcamera.CustomCamera(passed_dict) as testCam:
            self.assertEqual(testCam.get_rotation(), passed_dict["rotation"])

    def test_initialization_proper(self):
        passed_dict = dict([("rotation", 90)])
        with customcamera.CustomCamera(passed_dict) as testCam:
            self.assertEqual(testCam.get_rotation(), passed_dict["rotation"])

    def test_initialization_nonproper(self):
        passed_dict = dict([("rotation", 45)])
        with customcamera.CustomCamera(passed_dict) as testCam:
            self.assertNotEqual(testCam.get_rotation(), passed_dict["rotation"])
            self.assertEqual(testCam.get_rotation(), customcamera.CameraDefaults.CAMERA_ROTATION_DEFAULT)

"""
Tests that each option passed meets the criteria for default, valid and invalid parameters for ISO
"""
class TestCameraInitializationIso(unittest.TestCase):
    def test_initialization_default(self):
        passed_dict = dict([("iso", customcamera.CameraDefaults.CAMERA_ISO_DEFAULT)])
        with customcamera.CustomCamera(passed_dict) as testCam:
            self.assertEqual(testCam.get_iso(), passed_dict["iso"])

    def test_initialization_proper(self):
        passed_dict = dict([("iso", 100)])
        with customcamera.CustomCamera(passed_dict) as testCam:
            self.assertEqual(testCam.get_iso(), passed_dict["iso"])

    def test_initialization_nonproper(self):
        passed_dict = dict([("iso", 10)])
        with customcamera.CustomCamera(passed_dict) as testCam:
            self.assertNotEqual(testCam.get_iso(), passed_dict["iso"])
            self.assertEqual(testCam.get_iso(), customcamera.CameraDefaults.CAMERA_ISO_DEFAULT)

"""
Tests that each option passed meets the criteria for default, valid and invalid parameters for Brightness
"""
class TestCameraInitializationBrightness(unittest.TestCase):
    def test_initialization_default(self):
        passed_dict = dict([("brightness", customcamera.CameraDefaults.CAMERA_BRIGHTNESS_DEFAULT)])
        with customcamera.CustomCamera(passed_dict) as testCam:
            self.assertEqual(testCam.get_brightness(), passed_dict["brightness"])

    def test_initialization_proper(self):
        passed_dict = dict([("brightness", 100)])
        with customcamera.CustomCamera(passed_dict) as testCam:
            self.assertEqual(testCam.get_brightness(), passed_dict["brightness"])

    def test_initialization_nonproper(self):
        passed_dict = dict([("brightness", 1000)])
        with customcamera.CustomCamera(passed_dict) as testCam:
            self.assertNotEqual(testCam.get_brightness(), passed_dict["brightness"])
            self.assertEqual(testCam.get_brightness(), customcamera.CameraDefaults.CAMERA_BRIGHTNESS_DEFAULT)

"""
Tests that each option passed meets the criteria for default, valid and invalid parameters for Contrast
"""
class TestCameraInitializationContrast(unittest.TestCase):
    def test_initialization_default(self):
        passed_dict = dict([("contrast", customcamera.CameraDefaults.CAMERA_CONTRAST_DEFAULT)])
        with customcamera.CustomCamera(passed_dict) as testCam:
            self.assertEqual(testCam.get_contrast(), passed_dict["contrast"])

    def test_initialization_proper(self):
        passed_dict = dict([("contrast", 100)])
        with customcamera.CustomCamera(passed_dict) as testCam:
            self.assertEqual(testCam.get_contrast(), passed_dict["contrast"])

    def test_initialization_nonproper(self):
        passed_dict = dict([("contrast", 1000)])
        with customcamera.CustomCamera(passed_dict) as testCam:
            self.assertNotEqual(testCam.get_contrast(), passed_dict["contrast"])
            self.assertEqual(testCam.get_contrast(), customcamera.CameraDefaults.CAMERA_CONTRAST_DEFAULT)

"""
Tests that each option passed meets the criteria for default, valid and invalid parameters for Saturation
"""
class TestCameraInitializationSaturation(unittest.TestCase):
    def test_initialization_default(self):
        passed_dict = dict([("saturation", customcamera.CameraDefaults.CAMERA_SATURATION_DEFAULT)])
        with customcamera.CustomCamera(passed_dict) as testCam:
            self.assertEqual(testCam.get_saturation(), passed_dict["saturation"])

    def test_initialization_proper(self):
        passed_dict = dict([("saturation", 100)])
        with customcamera.CustomCamera(passed_dict) as testCam:
            self.assertEqual(testCam.get_saturation(), passed_dict["saturation"])

    def test_initialization_nonproper(self):
        passed_dict = dict([("saturation", 1000)])
        with customcamera.CustomCamera(passed_dict) as testCam:
            self.assertNotEqual(testCam.get_saturation(), passed_dict["saturation"])
            self.assertEqual(testCam.get_saturation(), customcamera.CameraDefaults.CAMERA_SATURATION_DEFAULT)

"""
Tests that each option passed meets the criteria for default, valid and invalid parameters for Stabilization
"""
class TestCameraInitializationStabilization(unittest.TestCase):
    def test_initialization_default(self):
        passed_dict = dict([("stabilization", customcamera.CameraDefaults.CAMERA_STABILIZATION_DEFAULT)])
        with customcamera.CustomCamera(passed_dict) as testCam:
            self.assertEqual(testCam.get_stabilization(), passed_dict["stabilization"])

    def test_initialization_proper(self):
        passed_dict = dict([("stabilization", True)])
        with customcamera.CustomCamera(passed_dict) as testCam:
            self.assertEqual(testCam.get_stabilization(), passed_dict["stabilization"])

    def test_initialization_nonproper(self):
        passed_dict = dict([("stabilization", 10)])
        with customcamera.CustomCamera(passed_dict) as testCam:
            self.assertNotEqual(testCam.get_stabilization(), passed_dict["stabilization"])
            self.assertEqual(testCam.get_stabilization(), customcamera.CameraDefaults.CAMERA_STABILIZATION_DEFAULT)


"""
Entry point if running all. We cannot do this though because of concurrent tests in package accessing picamera concurrently.
"""
if __name__ == '__main__':
    unittest.main()
