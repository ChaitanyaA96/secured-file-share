import React, { useState, useEffect } from 'react';
import { useDispatch, useSelector } from 'react-redux';
import { login, verifyMFA, enableMFA } from '../../actions/auth';
import { Form, Input, Button, Card, Typography, message } from 'antd';
import { Navigate } from 'react-router-dom';
import QRCodeReact from "react-qr-code";

const { Title, Text } = Typography;

const Login = () => {
  const [form] = Form.useForm();
  const [otpForm] = Form.useForm();
  const dispatch = useDispatch();
  const [currentStep, setCurrentStep] = useState(1); // Step 1: Login, Step 2: MFA, Step 3: MFA Setup
  const [otpUrl, setOtpUrl] = useState('');
  const isAuthenticated = useSelector((state) => state.auth.isAuthenticated);

  const onLogin = async (values) => {
    const { username, password } = values;
    try {
      const response = await dispatch(login(username, password));

      if (response.mfaSetupRequired) {
        setOtpUrl(response.otpUrl);
        setCurrentStep(3); // Move to MFA setup
      } else if (response.mfaRequired) {
        setCurrentStep(2); // Move to MFA verification
      } else {
        message.success('Login successful!');
      }
    } catch (error) {
      message.error('Login failed. Please check your credentials.');
    }
  };

  const onMfaSubmit = async (values) => {
    const { otp } = values;
    try {
      await dispatch(verifyMFA(otp));
      message.success('Login successful!');
    } catch (error) {
      message.error('Invalid OTP. Please try again.');
    }
  };

  const onMfaSetup = async (values) => {
    const { otp } = values;
    try {
      await dispatch(enableMFA(otp));
      message.success('MFA enabled successfully! Please log in again.');
      setCurrentStep(1); // Return to login
    } catch (error) {
      message.error('Failed to enable MFA. Please try again.');
    }
  };

  useEffect(() => {
    setCurrentStep(1);
  }, []);

  if (isAuthenticated) {
    return <Navigate to="/" />;
  }

  return (
    <div style={styles.container}>
      <Card style={styles.card} bordered={false}>
        <Title level={2} style={styles.title}>
          {currentStep === 3
            ? 'Set Up MFA'
            : currentStep === 2
            ? 'Verify MFA'
            : 'Login'}
        </Title>

        {currentStep === 1 && (
          <Form form={form} onFinish={onLogin} layout="vertical" name="loginForm">
            <Form.Item
              label="Username"
              name="username"
              rules={[{ required: true, message: 'Please input your username!' }]}
            >
              <Input placeholder="Enter your username" />
            </Form.Item>
            <Form.Item
              label="Password"
              name="password"
              rules={[{ required: true, message: 'Please input your password!' }]}
            >
              <Input.Password placeholder="Enter your password" />
            </Form.Item>
            <Form.Item>
              <Button type="primary" htmlType="submit" block>
                Login
              </Button>
            </Form.Item>
          </Form>
        )}

        {currentStep === 2 && (
          <Form form={otpForm} onFinish={onMfaSubmit} layout="vertical" name="mfaForm">
            <Form.Item
              label="OTP"
              name="otp"
              rules={[{ required: true, message: 'Please input the OTP!' }]}
            >
              <Input placeholder="Enter the OTP sent to your device" />
            </Form.Item>
            <Form.Item>
              <Button type="primary" htmlType="submit" block>
                Verify
              </Button>
            </Form.Item>
          </Form>
        )}

        {currentStep === 3 && (
          <div>
            <p>Scan this QR code with your authenticator app:</p>
            <QRCodeReact value={otpUrl} size={256} />
            <Form
              form={otpForm}
              onFinish={onMfaSetup}
              layout="vertical"
              name="mfaSetupForm"
            >
              <Form.Item
                label="First OTP"
                name="otp"
                rules={[{ required: true, message: 'Please input the OTP!' }]}
              >
                <Input placeholder="Enter the OTP from your authenticator app" />
              </Form.Item>
              <Form.Item>
                <Button type="primary" htmlType="submit" block>
                  Enable MFA
                </Button>
              </Form.Item>
            </Form>
          </div>
        )}
      </Card>
    </div>
  );
};

const styles = {
  container: {
    display: 'flex',
    justifyContent: 'center',
    alignItems: 'center',
    minHeight: '100vh',
    backgroundColor: '#f0f2f5',
  },
  card: {
    width: 400,
    padding: '20px',
  },
  title: {
    textAlign: 'center',
    marginBottom: '20px',
  },
  qrCode: {
    display: 'block',
    margin: '20px auto',
    maxWidth: '100%',
  },
};

export default Login;
