import React, { useState } from 'react';
import { useSelector, useDispatch } from 'react-redux';
import { Table, Button, Modal, message } from 'antd';
import FilePreview from './filepreview'; // Import the new component
import { accessSharedFileAuthenticated } from '../../actions/file';

const SharedWithMe = () => {
  const dispatch = useDispatch();
  const sharedWithMe = useSelector((state) => state.file.sharedWithMe);

  const [previewModalVisible, setPreviewModalVisible] = useState(false);
  const [previewContent, setPreviewContent] = useState(null);
  const [previewFileType, setPreviewFileType] = useState('');
  const [previewFileName, setPreviewFileName] = useState('');

  const handleFileAction = async (file) => {
    try {
      const linkUUID = file.shared_link.split('/').pop();
      const response = await dispatch(accessSharedFileAuthenticated(linkUUID));

      const contentType = response.headers?.['content-type'];
      //const fileUrl = URL.createObjectURL(response.data);
      const correctedBlob = new Blob([response.data], { type: contentType });
      const blobUrl = URL.createObjectURL(correctedBlob);

      if (file.share_type === 'view') {
        const supportedTypes = ['image/png', 'image/jpeg', 'image/jpg', 'video/mp4', 'application/pdf'];
        if (supportedTypes.includes(contentType)) {
          setPreviewContent(blobUrl);
          setPreviewFileType(contentType);
          setPreviewFileName(file.file_name);
          setPreviewModalVisible(true);
        } else {
          message.warning('File type not supported for preview.');
        }
      } else {
        triggerFileDownload(response.data, file.file_name);
      }
    } catch (err) {
      console.error('Error accessing shared file:', err);
      message.error('Failed to access the shared file. Please try again.');
    }
  };

    const columns = [
    { title: 'File Name', dataIndex: 'file_name', key: 'file_name' },
    { title: 'Shared By', dataIndex: 'shared_by', key: 'shared_by' },
    { title: 'Shared At', dataIndex: 'shared_at', key: 'shared_at' },
    { title: 'Expires At', dataIndex: 'expires_at', key: 'expires_at' },
    {
      title: 'Actions',
      key: 'actions',
      render: (_, file) => (
        <Button type="link" onClick={() => handleFileAction(file)}>
          {file.share_type === 'view' ? 'View' : 'Download'}
        </Button>
      ),
    },
  ];
  return (
    <>
      <Table dataSource={sharedWithMe} columns={columns} rowKey="id" />
      <Modal
        title={previewFileName}
        open={previewModalVisible}
        footer={null}
        onCancel={() => {
          URL.revokeObjectURL(previewContent); // Cleanup Blob URL
          setPreviewModalVisible(false);
          setPreviewContent(null);
        }}
        destroyOnClose
        width={900}
      >
        <FilePreview contentUrl={previewContent} fileType={previewFileType} fileName={previewFileName} />
      </Modal>
    </>
  );
};

export default SharedWithMe;






// import React, { useState } from 'react';
// import { useSelector, useDispatch } from 'react-redux';
// import { Table, Button, Modal, message } from 'antd';
// import { accessSharedFileAuthenticated } from '../../actions/file';

// const SharedWithMe = () => {
//   const dispatch = useDispatch();
//   const sharedWithMe = useSelector((state) => state.file.sharedWithMe);

//   const [previewModalVisible, setPreviewModalVisible] = useState(false);
//   const [previewContent, setPreviewContent] = useState(null);
//   const [previewFileType, setPreviewFileType] = useState('');
//   const [previewFileName, setPreviewFileName] = useState('');

//   const handleFileAction = async (file) => {
//     try {
//       const linkUUID = file.shared_link.split('/').pop();
//       const response =await dispatch(accessSharedFileAuthenticated(linkUUID));

//       const contentType = response.headers?.['content-type'] || 'application/octet-stream';
//       const fileUrl = URL.createObjectURL(response.data);

//       if (file.share_type === 'view') {
//         // Handle supported file types for preview
//         const supportedTypes = ['image/png', 'image/jpeg', 'image/jpg', 'video/mp4', 'application/pdf'];
//         if (supportedTypes.includes(contentType)) {
//           setPreviewContent(fileUrl);
//           setPreviewFileType(contentType);
//           setPreviewFileName(file.file_name);
//           setPreviewModalVisible(true);
//         } else {
//           message.warning('File type not supported for preview. Downloading the file.');
//           triggerFileDownload(fileBlob, file.file_name);
//         }
//       } else {
//         // Trigger download for non-view action
//         triggerFileDownload(fileBlob, file.file_name);
//       }
//     } catch (err) {
//       console.error('Error accessing shared file:', err);
//       message.error('Failed to access the shared file. Please try again.');
//     }
//   };

//   const triggerFileDownload = (fileBlob, fileName) => {
//     const link = document.createElement('a');
//     link.href = URL.createObjectURL(fileBlob);
//     link.download = fileName;
//     document.body.appendChild(link);
//     link.click();
//     link.remove();
//   };

//   const renderPreview = () => {
//     const disableContextMenu = (event) => event.preventDefault();
//     if (previewFileType.startsWith('image/')) {
//       return <img src={previewContent} alt={previewFileName} style={{ width: '100%' }} onContextMenu={disableContextMenu} />;
//     }
//     if (previewFileType === 'application/pdf') {
//       return (
//         <div>
//           <iframe
//             src={previewContent}
//             title={previewFileName}
//             style={{ width: '100%', height: '600px', border: 'none' }}
//             onContextMenu={disableContextMenu}
//           ></iframe>
//         </div>
//       );
//     }
//     if (previewFileType === 'video/mp4') {
//       return <video controls src={previewContent} style={{ width: '100%' }} onContextMenu={disableContextMenu} />;
//     }
//     return <p>Preview not available for this file type.</p>;
//   };

//   const columns = [
//     { title: 'File Name', dataIndex: 'file_name', key: 'file_name' },
//     { title: 'Shared By', dataIndex: 'shared_by', key: 'shared_by' },
//     { title: 'Shared At', dataIndex: 'shared_at', key: 'shared_at' },
//     { title: 'Expires At', dataIndex: 'expires_at', key: 'expires_at' },
//     {
//       title: 'Actions',
//       key: 'actions',
//       render: (_, file) => (
//         <Button type="link" onClick={() => handleFileAction(file)}>
//           {file.share_type === 'view' ? 'View' : 'Download'}
//         </Button>
//       ),
//     },
//   ];

//   return (
//     <>
//       <Table dataSource={sharedWithMe} columns={columns} rowKey="id" />

//       <Modal
//         title={previewFileName}
//         open={previewModalVisible}
//         footer={null}
//         onCancel={() => {
//           URL.revokeObjectURL(previewContent); // Cleanup Blob URL
//           setPreviewModalVisible(false);
//           setPreviewContent(null);
//         }}
//         destroyOnClose
//         width={900}
//         styles={{ padding: 0 }}
//       >
//         {renderPreview()}
//       </Modal>
//     </>
//   );
// };

// export default SharedWithMe;
