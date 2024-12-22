import React from 'react'

const FilePreview = ({ contentUrl, fileType, fileName }) => {
  const disableContextMenu = (event) => event.preventDefault()

  const renderContent = () => {
    if (fileType.startsWith('image/')) {
      return (
        <img
          src={contentUrl}
          alt={fileName}
          style={{ width: '100%' }}
          onContextMenu={disableContextMenu}
        />
      )
    }

    if (fileType === 'application/pdf') {
      return (
        <iframe
          src={contentUrl}
          title={fileName}
          width="100%"
          height="500px"
          style={{ border: 'none' }}
          onContextMenu={disableContextMenu}
          //sandbox="allow-scripts allow-same-origin allow-forms allow-popups"
        ></iframe>
      )
    }

    if (fileType === 'video/mp4') {
      return (
        <video
          controls
          src={contentUrl}
          style={{ width: '100%' }}
          onContextMenu={disableContextMenu}
        />
      )
    }

    return <p>Preview not available for this file type.</p>
  }

  return <div>{renderContent()}</div>
}

export default FilePreview
