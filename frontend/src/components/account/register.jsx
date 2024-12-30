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
  const [passwordErrors, setPasswordErrors] = useState([]); // State for real-time password errors
  const [confirmPasswordError, setConfirmPasswordError] = useState(''); // State for confirm password error
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

  const validatePassword = (password) => {
    const errors = [];
    if (password.length < 15) {
      errors.push('Password must be at least 15 characters long.');
    }
    if (!/[a-z]/.test(password)) {
      errors.push('Password must include at least one lowercase letter.');
    }
    if (!/[A-Z]/.test(password)) {
      errors.push('Password must include at least one uppercase letter.');
    }
    if (!/\d/.test(password)) {
      errors.push('Password must include at least one number.');
    }
    if (!/[@$!%*?&#]/.test(password)) {
      errors.push(
        'Password must include at least one special character (@, $, !, %, *, ?, &, #).'
      );
    }
    return errors;
  };

  const onValuesChange = (_, allValues) => {
    const { first_name, last_name, email, password, password2 } = allValues;

    // Validate password in real time
    const errors = password ? validatePassword(password) : [];
    setPasswordErrors(errors);

    // Check if confirm password matches the main password
    if (password && password2 && password !== password2) {
      setConfirmPasswordError('Passwords do not match.');
    } else {
      setConfirmPasswordError('');
    }

    // Check if all required fields are filled and valid
    const isValid =
      first_name &&
      last_name &&
      email &&
      password &&
      password2 &&
      password === password2 &&
      errors.length === 0; // Ensure password meets all criteria
    setIsFormValid(isValid);
  };

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
                Registration successful! Please check your email for
                verification. You have 24 hours to verify your account. You will
                be redirected to the login page in 10 seconds.
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
                    rules={[
                      {
                        required: true,
                        message: 'Please enter your first name',
                      },
                    ]}
                  >
                    <Input placeholder="Enter your first name" />
                  </Form.Item>

                  <Form.Item
                    label="Last Name"
                    name="last_name"
                    rules={[
                      {
                        required: true,
                        message: 'Please enter your last name',
                      },
                    ]}
                  >
                    <Input placeholder="Enter your last name" />
                  </Form.Item>

                  <Form.Item
                    label="Email"
                    name="email"
                    rules={[
                      {
                        required: true,
                        type: 'email',
                        message: 'Please enter a valid email',
                      },
                    ]}
                  >
                    <Input placeholder="Enter your email" />
                  </Form.Item>

                  <Form.Item
                    label="Password"
                    name="password"
                    rules={[
                      {
                        required: true,
                        message: 'Please enter your password',
                      },
                    ]}
                  >
                    <Input.Password placeholder="Enter your password" />
                  </Form.Item>
                  {passwordErrors.length > 0 && (
                    <div
                      style={{
                        marginBottom: '10px',
                        color: 'red',
                        fontSize: '14px',
                      }}
                    >
                      {passwordErrors.map((error, index) => (
                        <div key={index}>{error}</div>
                      ))}
                    </div>
                  )}

                  <Form.Item
                    label="Confirm Password"
                    name="password2"
                    rules={[
                      {
                        required: true,
                        message: 'Please confirm your password',
                      },
                    ]}
                  >
                    <Input.Password placeholder="Confirm your password" />
                  </Form.Item>
                  {confirmPasswordError && (
                    <div
                      style={{
                        marginBottom: '10px',
                        color: 'red',
                        fontSize: '14px',
                      }}
                    >
                      {confirmPasswordError}
                    </div>
                  )}

                  <Form.Item>
                    <Button
                      type="primary"
                      htmlType="submit"
                      disabled={!isFormValid} // Disable form submission if invalid
                    >
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
