# ============================================================
# IBVAP - Video Reader Module (VideoSource Abstraction)
# Modular Video Ingestion for File & Future RTSP/ONVIF Sources
# ============================================================

import os
import cv2
import logging
from abc import ABC, abstractmethod

logger = logging.getLogger("IBVAP.VideoReader")

class VideoSource(ABC):
    """Abstract Base Class for Video Sources (File, RTSP, ONVIF)."""
    
    @abstractmethod
    def read_frame(self):
        """Read next frame from source."""
        pass
        
    @abstractmethod
    def get_metadata(self):
        """Get video source metadata (FPS, width, height, total_frames, duration)."""
        pass
        
    @abstractmethod
    def is_opened(self):
        """Check if source is open and active."""
        pass
        
    @abstractmethod
    def release(self):
        """Release underlying video capture resources."""
        pass

class FileVideoSource(VideoSource):
    """Direct Video File Reader supporting MP4, AVI, MOV, MKV."""
    
    def __init__(self, video_path: str):
        self.video_path = video_path
        self.cap = None
        self.fps = 30.0
        self.width = 1280
        self.height = 720
        self.total_frames = 0
        self.duration_sec = 0.0
        self.current_frame_idx = 0
        self._init_capture()

    def _init_capture(self):
        if not os.path.exists(self.video_path):
            logger.error(f"Video file not found at: {self.video_path}")
            return
            
        self.cap = cv2.VideoCapture(self.video_path)
        if self.cap.isOpened():
            self.fps = self.cap.get(cv2.CAP_PROP_FPS) or 30.0
            self.width = int(self.cap.get(cv2.CAP_PROP_FRAME_WIDTH)) or 1280
            self.height = int(self.cap.get(cv2.CAP_PROP_FRAME_HEIGHT)) or 720
            self.total_frames = int(self.cap.get(cv2.CAP_PROP_FRAME_COUNT)) or 0
            if self.fps > 0 and self.total_frames > 0:
                self.duration_sec = round(self.total_frames / self.fps, 2)
            logger.info(f"Loaded Video File: {self.video_path} ({self.width}x{self.height} @ {self.fps:.1f} FPS, {self.total_frames} frames, {self.duration_sec}s)")

    def read_frame(self):
        if not self.cap or not self.cap.isOpened():
            return False, None
            
        ret, frame = self.cap.read()
        if not ret or frame is None:
            # Auto-loop video file for seamless real-time processing
            self.cap.set(cv2.CAP_PROP_POS_FRAMES, 0)
            self.current_frame_idx = 0
            ret, frame = self.cap.read()
            
        if ret and frame is not None:
            self.current_frame_idx += 1
            
        return ret, frame

    def get_metadata(self):
        return {
            'video_path': self.video_path,
            'fps': self.fps,
            'width': self.width,
            'height': self.height,
            'total_frames': self.total_frames,
            'duration_sec': self.duration_sec,
            'current_frame_idx': self.current_frame_idx,
            'progress_percent': round((self.current_frame_idx / max(1, self.total_frames)) * 100, 1)
        }

    def seek(self, frame_idx: int):
        if self.cap and self.cap.isOpened():
            self.cap.set(cv2.CAP_PROP_POS_FRAMES, frame_idx)
            self.current_frame_idx = frame_idx

    def is_opened(self):
        return self.cap is not None and self.cap.isOpened()

    def release(self):
        if self.cap:
            self.cap.release()
            self.cap = None
