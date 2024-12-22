import React, { useState } from 'react';
import { useSelector, useDispatch } from 'react-redux';
import { Table, Button, Modal, Input, Upload, message } from 'antd';
import { UploadOutlined } from '@ant-design/icons';
import { uploadFile, downloadFile } from '../../actions/file'; // Import both actions
import { ShareAltOutlined } from '@ant-design/icons';
import FileShareModal from './fileshare';

const MyFiles = () => {
  const myFiles = useSelector((state) => state.file.myFiles); // Fetch file list from Redux state
  const dispatch = useDispatch();

  const [uploadModalVisible, setUploadModalVisible] = useState(false);
  const [selectedFile, setSelectedFile] = useState(null);
  const [description, setDescription] = useState('');
  const [fileList, setFileList] = useState([]); // Manage file list for the Upload component
  const [shareModalVisible, setShareModalVisible] = useState(false);
  const [shareType, setShareType] = useState(''); // Track share type
  // Handle file selection
  const handleFileChange = ({ file, fileList }) => {
    if (file) {
      setSelectedFile(file); // Update the selected file
    }
    setFileList(fileList); // Update the file list
    console.log('Selected File:', file);
    console.log('File List:', fileList);
  };

  // Handle upload submission
  const handleUpload = () => {
    if (!selectedFile) {
      message.error('Please select a file to upload!');
      return;
    }

    // Create form data to send to the backend
    const formData = new FormData();
    formData.append('file', selectedFile);
    formData.append('description', description || '');
    formData.append('name', selectedFile.name);
    dispatch(uploadFile(formData))
      .then(() => {
        message.success('File uploaded successfully!');
        // Reset state after successful upload
        setFileList([]);
        setSelectedFile(null);
        setDescription('');
        setUploadModalVisible(false);
      })
      .catch(() => {
        message.error('Failed to upload file!');
      });
  };

  const handleShare = (file, type) => {
    setSelectedFile(file); // Store file to share
    setShareModalVisible(true); // Show Share Modal
    setShareType(type); // Set share type
  };

  // Handle file download
  const handleDownload = (fileId, fileName) => {
    dispatch(downloadFile(fileId, fileName))
      .then(() => {
        message.success(`${fileName} downloaded successfully!`);
      })
      .catch(() => {
        message.error(`Failed to download ${fileName}!`);
      });
  };

  const columns = [
    { title: 'File Name', dataIndex: 'name', key: 'name' },
    {
      title: 'Actions',
      key: 'actions',
      render: (_, file) => (
        <>
        <Button
          type="link"
          onClick={() => handleDownload(file.id, file.name)} // Pass file ID and name
        >
          Download
        </Button>
         <Button type="link" icon={<ShareAltOutlined />} onClick={() => handleShare(file, 'share')}>
         Share
        </Button>
        <Button type="link" icon={<ShareAltOutlined />} onClick={() => handleShare(file, 'public')}>
         Public Share
        </Button>
        </>
      ),
    },
  ];

  return (
    <div>
      <Button
        type="primary"
        icon={<UploadOutlined />}
        onClick={() => setUploadModalVisible(true)}
      >
        Upload File
      </Button>

      <Table
        dataSource={myFiles}
        columns={columns}
        rowKey="id"
        style={{ marginTop: '20px' }}
      />

      <Modal
        title="Upload File"
        visible={uploadModalVisible}
        onOk={handleUpload}
        onCancel={() => {
          setUploadModalVisible(false);
          setFileList([]); // Reset file list on modal close
          setSelectedFile(null); // Reset selected file
          setDescription(''); // Reset description
        }}
        okText="Upload"
      >
        <Upload
          beforeUpload={() => false} // Prevent auto upload
          onChange={handleFileChange}
          fileList={fileList} // Manage file list state
          accept="*/*" // Specify accepted file types (e.g., ".pdf, .docx")
          showUploadList={true}
        >
          <Button icon={<UploadOutlined />}>Select File</Button>
        </Upload>
        <Input
          placeholder="Enter description (optional)"
          value={description}
          onChange={(e) => setDescription(e.target.value)}
          style={{ marginTop: '10px' }}
        />
      </Modal>

      <FileShareModal
        modal={{
          isVisible: shareModalVisible,
          modalType: shareType,
        }}
        dispatch={dispatch}
        file={selectedFile} // Pass the selected file to the modal
        onClose={() => setShareModalVisible(false)} // Close the modal
      />
    </div>
  );
};

export default MyFiles;
