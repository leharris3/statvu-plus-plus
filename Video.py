class Video:
    """Class representing a full-length video replay.""""

    def __init__(self, title: str, network: str) -> None:
        self.title = title
        self.path = "unprocessed_videos/" + self.title
        self.is_normalized = False
        
    def normalize(self) -> Bool:
        # Normalize a video.
        return False
        
    def move_to_processed_dir(self) -> Bool:
    
        return False
    
        
        
    
        
