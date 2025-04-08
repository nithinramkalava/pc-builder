import sys
import os

# Add the parent directory (src/) to the path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from recommendation_system import PCRecommendationSystem

print(dir(PCRecommendationSystem))