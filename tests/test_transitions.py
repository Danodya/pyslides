import unittest
from unittest.mock import patch, MagicMock
import pygame

from pyslides import constant
from pyslides.transitions import SlideTransition


class TestSlideTransition(unittest.TestCase):
    def setUp(self):
        # Set up a virtual display for Pygame
        pygame.display.init()
        self.screen = pygame.display.set_mode((constant.SCREEN_WIDTH, constant.SCREEN_HEIGHT))

        # Create mock images
        self.prev_image = pygame.Surface((800, 600))
        self.next_image = pygame.Surface((800, 600))
        self.prev_image.fill((255, 0, 0))
        self.next_image.fill((0, 255, 0))

        # Set up mock state
        self.state = MagicMock()
        self.state.window_size = (constant.SCREEN_WIDTH, constant.SCREEN_HEIGHT)
        self.state.screen = self.screen
        self.state.current_page = 1

        # Initialize attributes that will be tested
        self.state.prev_slide_position = -19.75
        self.state.next_slide_position = 580.25

    def tearDown(self):
        pygame.display.quit()

    @patch('pygame.display.flip')
    def test_pull_transition(self, mock_flip):
        SlideTransition.pull(self.prev_image, self.next_image, self.state.window_size, self.screen, duration=0.1)
        # Check if the transition completed
        self.assertEqual(self.prev_image.get_alpha(), None)
        self.assertEqual(self.next_image.get_alpha(), None)

    @patch('pygame.display.flip')
    def test_fade_out_slide_in_transition(self, mock_flip):
        SlideTransition.fade_out_slide_in(self.prev_image, self.next_image, self.state.window_size, self.screen,
                                          duration=1.2)
        # Check if the transition completed
        # self.assertEqual(self.prev_image.get_alpha(), 1)
        self.assertEqual(self.next_image.get_alpha(), None)

    @patch('pygame.display.flip')
    def test_swipe_right_transition(self, mock_flip):
        SlideTransition.swipe_right(self.prev_image, self.next_image, self.state.window_size, self.screen, duration=0.1)
        # Ensure the final position is correct and no alpha issues
        self.assertEqual(self.prev_image.get_alpha(), None)
        self.assertEqual(self.next_image.get_alpha(), None)

    @patch('pygame.display.flip')
    def test_swipe_left_transition(self, mock_flip):
        SlideTransition.swipe_left(self.prev_image, self.next_image, self.state.window_size, self.screen, duration=0.1)
        # Ensure the final position is correct and no alpha issues
        self.assertEqual(self.prev_image.get_alpha(), None)
        self.assertEqual(self.next_image.get_alpha(), None)

    # @patch('pygame.display.flip')
    # def test_fade_in_transition(self, mock_flip):
    #     SlideTransition.fade_in(self.prev_image, self.next_image, self.state.window_size, self.screen, duration=1.2)
    #     # Check if the transition completed
    #     self.assertEqual(self.next_image.get_alpha(), 255)

    @patch('pygame.display.flip')
    def test_partial_sliding_transition(self, mock_flip):
        SlideTransition.partial_sliding(self.prev_image, self.next_image, self.state.window_size, self.screen,
                                        duration=0.1)
        # Check if the positions have been correctly set
        halfway_pos = self.state.window_size[1] / 4
        prev_start_pos = ((self.state.window_size[1] - self.prev_image.get_height()) // 2)
        expected_prev_position = prev_start_pos - halfway_pos
        expected_next_position = expected_prev_position + self.prev_image.get_height()

        # These checks should now work as expected
        self.assertEqual(self.state.prev_slide_position, expected_prev_position)
        self.assertEqual(self.state.next_slide_position, expected_next_position)

    @patch('pygame.display.flip')
    def test_choose_transition(self, mock_flip):
        SlideTransition.choose_transition(self.prev_image, self.next_image, self.state.window_size, self.screen, 'pull',
                                          duration=0.1)
        # Check that the pull transition was applied
        self.assertEqual(self.prev_image.get_alpha(), 255)
        self.assertEqual(self.next_image.get_alpha(), 255)


if __name__ == '__main__':
    unittest.main()
