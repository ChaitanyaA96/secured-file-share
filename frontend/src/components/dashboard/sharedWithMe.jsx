import React from 'react';
import { useSelector } from 'react-redux';
import { Table, Button } from 'antd';

const SharedWithMe = () => {
  const sharedWithMe = useSelector((state) => state.file.sharedWithMe);

  const columns = [
    { title: 'File Name', dataIndex: 'file_name', key: 'file_name' }, // Map to `file_name`
    { title: 'Shared By', dataIndex: 'shared_by', key: 'shared_by' }, // Map to `shared_by`
    { title: 'Shared At', dataIndex: 'shared_at', key: 'shared_at' }, // Map to `shared_at`
    { title: 'Expires At', dataIndex: 'expires_at', key: 'expires_at' }, // Map to `expires_at`
    {
      title: 'Actions',
      key: 'actions',
      render: (_, file) => (
        <Button
          type="link"
          onClick={() => {
            if (file.share_type === 'view') {
              console.log(`Viewing file at ${file.shared_link}`);
              window.open(file.shared_link, '_blank'); // Open file in a new tab
            } else {
              console.log(`Downloading file from ${file.shared_link}`);
              window.location.href = file.shared_link; // Download file
            }
          }}
        >
          {file.share_type === 'view' ? 'View' : 'Download'}
        </Button>
      ),
    },
  ];

  return <Table dataSource={sharedWithMe} columns={columns} rowKey="id" />;
};

export default SharedWithMe;
