import React, { useState } from 'react'
import { Modal, Upload, Button, Input, message } from 'antd'
import { UploadOutlined } from '@ant-design/icons'
import { useDispatch } from 'react-redux'
import { uploadFile } from '../../actions/file'

const UploadFileModal = ({ visible, onClose }) => {
  const [selectedFile, setSelectedFile] = useState(null)
  const [description, setDescription] = useState('')
  const dispatch = useDispatch()

  const handleFileChange = ({ file }) => {
    setSelectedFile(file)
  }

  const handleUpload = () => {
    if (!selectedFile) {
      message.error('Please select a file to upload!')
      return
    }

    const formData = new FormData()
    formData.append('file', selectedFile)
    formData.append('description', description || '')

    dispatch(uploadFile(formData))
      .then(() => {
        message.success('File uploaded successfully!')
        onClose()
      })
      .catch(() => {
        message.error('Failed to upload file!')
      })

    setSelectedFile(null)
    setDescription('')
  }

  return (
    <Modal
      title="Upload File"
      visible={visible}
      onOk={handleUpload}
      onCancel={onClose}
      okText="Upload"
    >
      <Upload
        beforeUpload={() => false} // Prevent auto-upload
        onChange={handleFileChange}
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
  )
}

export default UploadFileModal
