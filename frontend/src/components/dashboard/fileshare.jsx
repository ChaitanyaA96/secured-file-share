import { Modal, Form, Input, AutoComplete, DatePicker, Checkbox, Space, message } from 'antd';
import { useState } from 'react';
import { useDispatch } from 'react-redux';
import { shareFile } from '../../actions/file'; // Import the shareFile action
import moment from 'moment';

function FileShareModal({ modal = { isVisible: false, modalType: '' }, file, dispatch, onClose }) {
  const [form] = Form.useForm();
  const [options, setOptions] = useState([]);
  const reduxDispatch = useDispatch(); // Redux dispatch for sharing files

  const onSearch = (value) => {
    if (value) {
      // Mock API call for suggestions
      setOptions([
        { value: 'user1@example.com' },
        { value: 'user2@example.com' },
      ]);
    } else {
      setOptions([]);
    }
  };

  const handleOk = async () => {
    try {
      const values = await form.validateFields(); // Ensure form validation

      const expiresInHours = moment().diff(moment(values.expiryDate).local(), 'hours');

      console.log("time now", moment().local());
      console.log("time expiry", moment(values.expiryDate).local());
    if (expiresInHours < 0) {
        throw new Error('Expiry date must be in the future.');
      }
      const shareDetails = {
        file_id: file.id,
        share_type: values.shareType,
        shared_with: values.email,
        expires_in: expiresInHours, 
        public: values.public || false, 
        one_time: values.one_time || false, 
      };

      // Dispatch the shareFile action
      await reduxDispatch(shareFile(shareDetails));
      message.success(`File "${file.name}" shared successfully!`);
      dispatch({ type: 'HIDE_MODAL' });
      onClose();
    } catch (error) {
      console.error('Validation or share error:', error);
      if (error.errorFields) {
        message.error('Please correct the highlighted fields.');
      } else {
        message.error('Failed to share the file. Please try again.');
      }
    }
  };

  const handleCancel = () => {
    dispatch({ type: 'HIDE_MODAL' });
    onClose();
  };

  return (
    <Modal
      title={`Share File: ${file?.name || ''}`} // Show the selected file name
      open={modal.isVisible && modal.modalType === 'share'}
      onOk={handleOk}
      onCancel={handleCancel}
    >
      <Form form={form} layout="vertical" initialValues={{ public: false, one_time: false }}>
        <Form.Item
          label="Email/Name"
          name="email"
          rules={[{ required: true, message: 'Please enter an email or name!' }]}
        >
          <AutoComplete
            options={options}
            onSearch={onSearch}
            placeholder="Enter email or name"
          />
        </Form.Item>
        <Form.Item
          label="Expiry Date"
          name="expiryDate"
          rules={[{ required: true, message: 'Please select an expiry date!' }]}
        >
          <DatePicker showTime style={{ width: '100%' }} />
        </Form.Item>
        <Form.Item
          label="Share Type"
          name="shareType"
          rules={[{ required: true, message: 'Please select a share type!' }]}
        >
          <Space.Compact>
            <Checkbox value="view">View</Checkbox>
            <Checkbox value="download">Download</Checkbox>
          </Space.Compact>
        </Form.Item>
        <Form.Item
          label="Public Access"
          name="public"
          valuePropName="checked"
        >
          <Checkbox>Allow Public Access</Checkbox>
        </Form.Item>
        <Form.Item
          label="One-Time Access"
          name="one_time"
          valuePropName="checked"
        >
          <Checkbox>Allow One-Time Access</Checkbox>
        </Form.Item>
      </Form>
    </Modal>
  );
}

export default FileShareModal;
