import React, { useState, useRef, useEffect } from 'react';
import axios from 'axios';
import styled from 'styled-components';

const DashboardContainer = styled.div`
  max-width: 800px;
  margin: auto;
  padding: 20px;
  background-color: #f9f9f9;
  border-radius: 10px;
  box-shadow: 0 0 10px rgba(0, 0, 0, 0.1);
`;

const FileInput = styled.input`
  display: none;
`;

const DropZone = styled.div`
  border: 2px dashed #3498db;
  padding: 20px;
  border-radius: 5px;
  cursor: pointer;
  margin-bottom: 20px;
`;

const ChooseFileButton = styled.label`
  background-color: #3498db;
  color: white;
  padding: 10px 15px;
  border: none;
  border-radius: 5px;
  cursor: pointer;
  margin-right: 10px;
`;

const UploadButton = styled.button`
  background-color: #4caf50;
  color: white;
  padding: 10px 15px;
  border: none;
  border-radius: 5px;
  cursor: pointer;
`;

const VideoContainer = styled.div`
  margin-top: 20px;
`;

const Dashboard = () => {
  const [file, setFile] = useState(null);
  const [imageUrl, setImageUrl] = useState(null);
  const [outputVideoUrl, setOutputVideoUrl] = useState(null);
  const [uploadProgress, setUploadProgress] = useState(0);
  const videoRef = useRef(null);
  const fileInputRef = useRef(null);

  axios.interceptors.response.use(
    (response) => {
      return response;
    },
    (error) => {
      return Promise.reject(error);
    }
  );

  const handleFileUpload = (event) => {
    const selectedFile = event.target.files[0];
    setFile(selectedFile);
  };

  const handleChooseFileClick = () => {
    if (fileInputRef.current) {
      fileInputRef.current.click();
    }
  };

  const handleUploadButtonClick = () => {
    if (file) {
      const formData = new FormData();
      formData.append('video', file);

      axios.post('http://localhost:5000/process_video', formData, {
        responseType: 'arraybuffer',
        onUploadProgress: (progressEvent) => {
          const progress = Math.round((progressEvent.loaded / progressEvent.total) * 100);
          setUploadProgress(progress);
        },
      })
        .then(response => {
          const blob = new Blob([response.data], { type: 'image/jpeg' });
          const url = URL.createObjectURL(blob);
          setImageUrl(url);
        })
        .catch(error => {
          console.error('Error processing image:', error);
        });
    } else {
      alert('Please select an image file before uploading.');
    }
  };

  const handleDrop = (event) => {
    event.preventDefault();

    if (event.dataTransfer.items) {
      for (let i = 0; i < event.dataTransfer.items.length; i++) {
        if (event.dataTransfer.items[i].kind === 'file') {
          const file = event.dataTransfer.items[i].getAsFile();
          setFile(file);
          break;
        }
      }
    } else {
      for (let i = 0; event.dataTransfer.files && i < event.dataTransfer.files.length; i++) {
        const file = event.dataTransfer.files[i];
        setFile(file);
        break;
      }
    }
  };

  const handleDragOver = (event) => {
    event.preventDefault();
  };

  const handleRefreshButtonClick = () => {
    // Reset states and reload the video
    setFile(null);
    setImageUrl(null);
    setOutputVideoUrl(null);
    setUploadProgress(0);

    // Add logic to reload the video (you may need to fetch the updated video URL)
    const filename = 'YOUR_OUTPUT_FILENAME'; // replace with the actual filename
    setOutputVideoUrl(`http://localhost:5000/uploads/${filename}`);
  };

  useEffect(() => {
    return () => {
      if (imageUrl) {
        URL.revokeObjectURL(imageUrl);
      }
    };
  }, [imageUrl]);

  useEffect(() => {
    const filename = 'YOUR_OUTPUT_FILENAME';
    setOutputVideoUrl(`http://localhost:5000/uploads/${filename}`);
  }, [imageUrl]);

  return (
    <DashboardContainer>
      <h2>Object Detection Dashboard</h2>
      <DropZone
        onDrop={handleDrop}
        onDragOver={handleDragOver}
      >
        Drop image here or&nbsp;
        <ChooseFileButton onClick={handleChooseFileClick}>
          Choose File
        </ChooseFileButton>
      </DropZone>
      <FileInput
        type="file"
        accept="image/*"
        onChange={handleFileUpload}
        id="fileInput"
        ref={fileInputRef}
      />
      <UploadButton onClick={handleUploadButtonClick} disabled={!file}>
        Upload Image
      </UploadButton>
      {uploadProgress > 0 && uploadProgress < 100 && (
        <div>
          Uploading: {uploadProgress}%
          <progress value={uploadProgress} max="100" />
        </div>
      )}
      <VideoContainer>
        {outputVideoUrl && (
          <div>
            <video ref={videoRef} controls width="100%">
              <source src={outputVideoUrl} type="video/mp4" />
              Your browser does not support the video tag.
            </video>
            <button onClick={handleRefreshButtonClick}>
              Refresh Video
            </button>
          </div>
        )}
      </VideoContainer>
    </DashboardContainer>
  );
};

export default Dashboard;
