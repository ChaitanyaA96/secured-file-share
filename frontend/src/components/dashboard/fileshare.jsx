import {
  Modal,
  Form,
  Input,
  AutoComplete,
  Checkbox,
  message,
  Button,
} from 'antd'
import { useState, useEffect } from 'react'
import { useDispatch } from 'react-redux'
import {
  shareFileAuthenticated,
  shareFilePublic,
  sendEmail,
  getPublicShareDetails,
} from '../../actions/file'
import moment from 'moment'

function FileShareModal({
  modal = { isVisible: false, modalType: '' },
  file,
  dispatch,
  onClose,
}) {
  const [form] = Form.useForm()
  const [publicShareForm] = Form.useForm()
  const reduxDispatch = useDispatch()
  const [shareDetails, setShareDetails] = useState(null)
  const [recipientEmail, setRecipientEmail] = useState('')
  const [loading, setLoading] = useState(false)

  // Check for existing public share details when modal opens
  useEffect(() => {
    if (modal.isVisible && modal.modalType === 'public' && file) {
      fetchPublicShareDetails()
    }
  }, [modal.isVisible, modal.modalType, file])

  const fetchPublicShareDetails = async () => {
    try {
      setLoading(true)
      const existingDetails = await reduxDispatch(
        getPublicShareDetails({ file_id: file.id }),
      )
      if (existingDetails) {
        setShareDetails(existingDetails)
      } else {
        setShareDetails(null) // Ensure no stale data
      }
    } catch (error) {
      //TODO
    } finally {
      setLoading(false)
    }
  }

  const handleOk = async () => {
    try {
      const values = await form.validateFields()
      const expiresInHours = moment(values.expiryDate)
        .local()
        .diff(moment().local(), 'hours')

      if (expiresInHours <= 0) {
        throw new Error('Expiry date must be in the future.')
      }

      const shareDetails = {
        file_id: file.id,
        share_type: values.shareType[0],
        shared_with: values.email,
        expires_in: expiresInHours,
        public: false,
        one_time: values.one_time || false,
      }

      await reduxDispatch(shareFileAuthenticated(shareDetails))
      message.success(`File "${file.name}" shared successfully!`)
      onClose()
    } catch (error) {
      //TODO
      message.error(
        error.message || 'Failed to share the file. Please try again.',
      )
    }
  }

  const handlePublicShare = async () => {
    try {
      const values = await publicShareForm.validateFields()
      const expiresInHours = moment(values.expiryDate)
        .local()
        .diff(moment().local(), 'hours')

      if (expiresInHours <= 0) {
        throw new Error('Expiry date must be in the future.')
      }

      const shareDetails = {
        file_id: file.id,
        expires_in: expiresInHours,
        passphrase: values.passphrase,
        share_type: 'download',
      }

      const res = await reduxDispatch(shareFilePublic(shareDetails))
      setShareDetails(res) // Store share details
      message.success('Public share link created successfully!')
    } catch (error) {
      //TODO
      message.error('Failed to create public share. Please try again.')
    }
  }

  const handleSendEmail = async () => {
    if (!recipientEmail) {
      message.error('Please enter a recipient email!')
      return
    }

    try {
      const emailData = {
        to: [recipientEmail],
        subject: 'Public Share Link',
        message: `Here are the public share details:\nLink: ${shareDetails?.shared_link}\nPassphrase: ${shareDetails?.passphrase}\nExpires at: ${shareDetails?.expires_at}`,
      }

      await reduxDispatch(sendEmail(emailData))
      message.success('Email sent successfully!')
    } catch (error) {
      //TODO
      message.error('Failed to send email. Please try again.')
    }
  }

  const handleCancel = () => {
    form.resetFields()
    publicShareForm.resetFields()
    setShareDetails(null) // Reset share details
    setRecipientEmail('') // Reset recipient email
    onClose()
  }

  return (
    <Modal
      title={
        modal.modalType === 'share'
          ? `Share File: ${file?.name || ''}`
          : `Create Public Share: ${file?.name || ''}`
      }
      open={modal.isVisible}
      onCancel={handleCancel}
      footer={null} // Custom footer for better control
    >
      {modal.modalType === 'share' ? (
        <Form
          form={form}
          layout="vertical"
          initialValues={{ public: false, one_time: false }}
          onFinish={handleOk}
        >
          <Form.Item
            label="Email/Name"
            name="email"
            rules={[
              { required: true, message: 'Please enter an email or name!' },
            ]}
          >
            <AutoComplete placeholder="Enter email or name" />
          </Form.Item>
          <Form.Item
            label="Expiry Date"
            name="expiryDate"
            rules={[
              { required: true, message: 'Please select an expiry date!' },
            ]}
          >
            <Input type="datetime-local" />
          </Form.Item>
          <Form.Item
            label="Share Type"
            name="shareType"
            rules={[{ required: true, message: 'Please select a share type!' }]}
          >
            <Checkbox.Group options={['view', 'download']} />
          </Form.Item>
          <Button type="primary" htmlType="submit">
            Share
          </Button>
        </Form>
      ) : (
        <>
          {loading ? (
            <p>Loading public share details...</p>
          ) : shareDetails ? (
            <div>
              <p>
                <strong>Link:</strong> {shareDetails.shared_link}
              </p>
              <p>
                <strong>Passphrase:</strong> {shareDetails.passphrase}
              </p>
              <p>
                <strong>Expires At:</strong> {shareDetails.expires_at}
              </p>
              <Input
                placeholder="Enter recipient email"
                value={recipientEmail}
                onChange={(e) => setRecipientEmail(e.target.value)}
              />
              <Button
                type="primary"
                onClick={handleSendEmail}
                style={{ marginTop: '10px' }}
              >
                Send via Email
              </Button>
            </div>
          ) : (
            <Form
              form={publicShareForm}
              layout="vertical"
              onFinish={handlePublicShare}
            >
              <Form.Item
                label="Expiry Date"
                name="expiryDate"
                rules={[
                  { required: true, message: 'Please select an expiry date!' },
                ]}
              >
                <Input type="datetime-local" />
              </Form.Item>
              <Button type="primary" htmlType="submit">
                Generate Link
              </Button>
            </Form>
          )}
        </>
      )}
    </Modal>
  )
}

export default FileShareModal
