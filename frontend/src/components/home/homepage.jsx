// src/pages/Home.js
import React from 'react'
import { Typography, Divider } from 'antd'

const { Title, Paragraph } = Typography

const Home = () => {
  return (
    <div>
      <div>
        <Title>Welcome to My File Sharing App</Title>
        <Paragraph>
          Securely share your files with ease. Upload your files and generate
          secure links now!
        </Paragraph>
      </div>

      <div>
        <Paragraph>
          Need help? Visit our <a href="/about">About</a> page or{' '}
          <a href="/upload">Upload</a> a file now.
        </Paragraph>
      </div>
    </div>
  )
}

export default Home
