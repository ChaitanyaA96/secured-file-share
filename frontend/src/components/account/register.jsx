import React, { useState, useEffect } from 'react';
import { Navigate } from 'react-router-dom';
import { useDispatch, useSelector } from 'react-redux';
import { Form, Input, Button, Card, Row, Col, message } from 'antd';
import { register } from '../../actions/auth';

const Register = () => {
  const [redirect, setRedirect] = useState(false);
  const [showSuccessMessage, setShowSuccessMessage] = useState(false);
  const [showErrorMessage, setShowErrorMessage] = useState(false);
  const [isFormValid, setIsFormValid] = useState(false); // State to manage form validity
  const errorMessage = useSelector((state) => state.auth.errorMessage);
  const dispatch = useDispatch();

  useEffect(() => {
    if (errorMessage) {
      setShowErrorMessage(true);
      const timer = setTimeout(() => setShowErrorMessage(false), 10000);
      return () => clearTimeout(timer); // Cleanup timer
    }
  }, [errorMessage]);

  useEffect(() => {
    if (showSuccessMessage) {
      const timer = setTimeout(() => {
        setRedirect(true); // Redirect after 10 seconds
        setShowSuccessMessage(false); // Reset state
      }, 10000);
      return () => clearTimeout(timer); // Cleanup timer
    }
  }, [showSuccessMessage]);

  const onFinish = (values) => {
    const { first_name, last_name, email, password, password2 } = values;

    if (password !== password2) {
      message.error('Passwords do not match');
    } else {
      const newUser = {
        first_name,
        last_name,
        password,
        email,
      };
      dispatch(register(newUser))
        .then(() => {
          setShowSuccessMessage(true); // Show success message
          setShowErrorMessage(false); // Reset error state
        })
        .catch(() => {
          setShowSuccessMessage(false); // Reset success state
        });
    }
  };

  const onValuesChange = (_, allValues) => {
    // Check if all required fields are filled
    const { first_name, last_name, email, password, password2 } = allValues;
    const isValid =
      first_name &&
      last_name &&
      email &&
      password &&
      password2 &&
      password === password2;
    setIsFormValid(isValid);
  };

  if (redirect) {
    return <Navigate to="/login" />;
  }

  return (
    <div className="container">
      <Row gutter={16}>
        <Col span={12} offset={6}>
          <Card className="mt-5">
            {showSuccessMessage ? (
              <div
                className="success-message"
                style={{
                  margin: '20px 0',
                  color: 'green',
                  textAlign: 'center',
                  fontSize: '18px',
                }}
              >
                Registration successful! Please check your email for verification.
                You have 24 hours to verify your account. You will be redirected to
                the login page in 10 seconds.
              </div>
            ) : (
              <>
                {showErrorMessage && (
                  <div
                    className="error-message"
                    style={{
                      marginBottom: '20px',
                      color: 'red',
                      textAlign: 'center',
                      fontSize: '18px',
                    }}
                  >
                    {errorMessage}
                  </div>
                )}
                <Form
                  layout="vertical"
                  onFinish={onFinish}
                  onValuesChange={onValuesChange} // Track form changes
                >
                  <Form.Item
                    label="First Name"
                    name="first_name"
                    rules={[{ required: true, message: 'Please enter your first name' }]}
                  >
                    <Input placeholder="Enter your first name" />
                  </Form.Item>

                  <Form.Item
                    label="Last Name"
                    name="last_name"
                    rules={[{ required: true, message: 'Please enter your last name' }]}
                  >
                    <Input placeholder="Enter your last name" />
                  </Form.Item>

                  <Form.Item
                    label="Email"
                    name="email"
                    rules={[{ required: true, type: 'email', message: 'Please enter a valid email' }]}
                  >
                    <Input placeholder="Enter your email" />
                  </Form.Item>

                  <Form.Item
                    label="Password"
                    name="password"
                    rules={[{ required: true, message: 'Please enter your password' }]}
                  >
                    <Input.Password placeholder="Enter your password" />
                  </Form.Item>

                  <Form.Item
                    label="Confirm Password"
                    name="password2"
                    rules={[{ required: true, message: 'Please confirm your password' }]}
                  >
                    <Input.Password placeholder="Confirm your password" />
                  </Form.Item>

                  <Form.Item>
                    <Button type="primary" htmlType="submit" disabled={!isFormValid}>
                      Register
                    </Button>
                  </Form.Item>
                </Form>
              </>
            )}
          </Card>
        </Col>
      </Row>
    </div>
  );
};

export default Register;
