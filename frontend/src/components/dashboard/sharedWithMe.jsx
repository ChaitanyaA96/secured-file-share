import React, { useState } from 'react'
import { useSelector, useDispatch } from 'react-redux'
import { Table, Button, Modal, message } from 'antd'
import FilePreview from './filepreview' // Import the new component
import { accessSharedFileAuthenticated } from '../../actions/file'

const SharedWithMe = () => {
  const dispatch = useDispatch()
  const sharedWithMe = useSelector((state) => state.file.sharedWithMe)

  const [previewModalVisible, setPreviewModalVisible] = useState(false)
  const [previewContent, setPreviewContent] = useState(null)
  const [previewFileType, setPreviewFileType] = useState('')
  const [previewFileName, setPreviewFileName] = useState('')

  const triggerFileDownload = (fileData, fileName) => {
    try {
      // Create a Blob for the file data
      const blob = new Blob([fileData])
      const fileUrl = URL.createObjectURL(blob)

      // Create a temporary anchor element
      const link = document.createElement('a')
      link.href = fileUrl
      link.download = fileName // Specify the filename for the downloaded file
      document.body.appendChild(link) // Append the link to the DOM temporarily

      // Programmatically click the link to trigger the download
      link.click()

      // Cleanup: Remove the link and revoke the Blob URL
      document.body.removeChild(link)
      URL.revokeObjectURL(fileUrl)
    } catch (error) {
      //TODO
      message.error('Failed to download the file. Please try again.')
    }
  }

  const handleFileAction = async (file) => {
    try {
      const linkUUID = file.shared_link.split('/').pop()
      const response = await dispatch(accessSharedFileAuthenticated(linkUUID))

      const contentType = response.headers?.['content-type']
      //const fileUrl = URL.createObjectURL(response.data);
      const correctedBlob = new Blob([response.data], { type: contentType })
      const blobUrl = URL.createObjectURL(correctedBlob)

      if (file.share_type === 'view') {
        const supportedTypes = [
          'image/png',
          'image/jpeg',
          'image/jpg',
          'video/mp4',
          'application/pdf',
        ]
        if (supportedTypes.includes(contentType)) {
          setPreviewContent(blobUrl)
          setPreviewFileType(contentType)
          setPreviewFileName(file.file_name)
          setPreviewModalVisible(true)
        } else {
          message.warning('File type not supported for preview.')
        }
      } else {
        triggerFileDownload(response.data, file.file_name)
      }
    } catch (err) {
      //TODO
      message.error('Failed to access the shared file. Please try again.')
    }
  }

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
  ]
  return (
    <>
      <Table dataSource={sharedWithMe} columns={columns} rowKey="id" />
      <Modal
        title={previewFileName}
        open={previewModalVisible}
        footer={null}
        onCancel={() => {
          URL.revokeObjectURL(previewContent) // Cleanup Blob URL
          setPreviewModalVisible(false)
          setPreviewContent(null)
        }}
        destroyOnClose
        width={900}
      >
        <FilePreview
          contentUrl={previewContent}
          fileType={previewFileType}
          fileName={previewFileName}
        />
      </Modal>
    </>
  )
}

export default SharedWithMe
