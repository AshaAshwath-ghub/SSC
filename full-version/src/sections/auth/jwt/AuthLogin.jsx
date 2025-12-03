import PropTypes from 'prop-types';
import React, { useEffect, useRef } from 'react';
import { Link as RouterLink, useSearchParams } from 'react-router-dom';
import ReCAPTCHA from 'react-google-recaptcha';

// material-ui
import Button from '@mui/material/Button';
import Checkbox from '@mui/material/Checkbox';
import FormControlLabel from '@mui/material/FormControlLabel';
import FormHelperText from '@mui/material/FormHelperText';
import Grid from '@mui/material/Grid';
import Link from '@mui/material/Link';
import InputAdornment from '@mui/material/InputAdornment';
import InputLabel from '@mui/material/InputLabel';
import OutlinedInput from '@mui/material/OutlinedInput';
import Stack from '@mui/material/Stack';
import Typography from '@mui/material/Typography';
import Box from '@mui/material/Box';
import CircularProgress from '@mui/material/CircularProgress';
import Alert from '@mui/material/Alert';

// third-party
import * as Yup from 'yup';
import { Formik } from 'formik';
import { preload } from 'swr';

// project imports
import IconButton from 'components/@extended/IconButton';
import AnimateButton from 'components/@extended/AnimateButton';

import useAuth from 'hooks/useAuth';

import { fetcher } from 'utils/axios';

// assets
import EyeOutlined from '@ant-design/icons/EyeOutlined';
import EyeInvisibleOutlined from '@ant-design/icons/EyeInvisibleOutlined';
import MobileOutlined from '@ant-design/icons/MobileOutlined';
import PhoneOutlined from '@ant-design/icons/PhoneOutlined';
import MessageOutlined from '@ant-design/icons/MessageOutlined';
import MailOutlined from '@ant-design/icons/MailOutlined';
import SafetyOutlined from '@ant-design/icons/SafetyOutlined';

// ============================|| JWT - LOGIN ||============================ //

export default function AuthLogin({ isDemo = false }) {
  const [checked, setChecked] = React.useState(false);
  const [mfaStatus, setMfaStatus] = React.useState(null); // 'pending', 'approved', 'denied', 'error', 'selection', 'otp_input'
  const [mfaToken, setMfaToken] = React.useState(null);
  const [mfaMessage, setMfaMessage] = React.useState('');
  const [availableMfaMethods, setAvailableMfaMethods] = React.useState([]);
  const [selectedMethod, setSelectedMethod] = React.useState(null);
  const [otpCode, setOtpCode] = React.useState('');
  const [otpError, setOtpError] = React.useState('');
  const [isVerifying, setIsVerifying] = React.useState(false);
  const [submittedOtp, setSubmittedOtp] = React.useState(null); // Store submitted OTP for polling
  const [otpBoxes, setOtpBoxes] = React.useState(['', '', '', '', '', '']); // 6 boxes for OTP
  const otpInputRefs = useRef([]);
  const pollingInterval = useRef(null);
  const recaptchaRef = useRef(null);

  const { login, verifyMFA } = useAuth();
  const recaptchaSiteKey = import.meta.env.VITE_APP_RECAPTCHA_SITE_KEY;

  const [showPassword, setShowPassword] = React.useState(false);
  const handleClickShowPassword = () => {
    setShowPassword(!showPassword);
  };

  const handleMouseDownPassword = (event) => {
    event.preventDefault();
  };

  const [searchParams] = useSearchParams();
  const auth = searchParams.get('auth'); // get auth and set route based on that

  // Trigger selected MFA method
  const triggerMfaMethod = async (method) => {
    try {
      console.log('Triggering MFA method:', method, 'with token:', mfaToken);

      setSelectedMethod(method);

      // Check if this is an OTP-based method
      const isOtpMethod = method === 'duo_sms' || method === 'email_otp' || method === 'twilio_sms' || method === 'totp';

      if (isOtpMethod) {
        // For OTP methods, show sending status temporarily
        setMfaStatus('pending');
        setMfaMessage('Sending verification code...');
      } else {
        // For push methods, show waiting screen
        setMfaStatus('pending');
        setMfaMessage('Sending authentication request...');
      }

      const apiUrl = (import.meta.env.VITE_APP_API_URL || 'http://localhost:3010').replace(/\/$/, '');
      const url = `${apiUrl}/api/v1/auth/mfa/trigger`;
      console.log('Calling endpoint:', url);

      const response = await fetch(url, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json'
        },
        body: JSON.stringify({
          mfa_token: mfaToken,
          method: method
        })
      });

      console.log('Trigger response status:', response.status);
      const data = await response.json();
      console.log('Trigger response data:', data);

      if (!response.ok) {
        throw new Error(data.detail || 'Failed to trigger MFA method');
      }

      console.log('MFA triggered successfully');

      if (isOtpMethod) {
        // For OTP methods, show input screen
        setMfaStatus('otp_input');
        setMfaMessage(data.message || 'Enter the verification code sent to you.');
        setOtpCode('');
        setOtpBoxes(['', '', '', '', '', '']);
        setOtpError('');
      } else {
        // For push methods, update message and start polling
        setMfaMessage(data.message || 'Please check your device for authentication request.');

        // Start polling for MFA status after a short delay
        setTimeout(() => {
          console.log('Starting MFA polling...');
          pollingInterval.current = setInterval(() => {
            pollMFAStatus(mfaToken);
          }, 3000);

          // Do initial poll
          pollMFAStatus(mfaToken);
        }, 2000);
      }

    } catch (error) {
      console.error('MFA trigger error:', error);
      setMfaStatus('error');

      // Extract error message from response
      let errorMessage = 'Failed to send authentication request. Please try again.';
      if (error.response?.data?.detail) {
        errorMessage = error.response.data.detail;
      } else if (error.message) {
        errorMessage = error.message;
      }

      setMfaMessage(errorMessage);
    }
  };

  // Poll MFA status
  const pollMFAStatus = async (token, passcode = null) => {
    try {
      console.log('========== POLLING MFA STATUS ==========');
      console.log('Token:', token);
      console.log('Passcode:', passcode);
      console.log('Selected Method:', selectedMethod);

      const result = await verifyMFA(token, passcode);

      console.log('========== POLL RESULT ==========');
      console.log('Full result:', JSON.stringify(result, null, 2));
      console.log('Status value:', result.status);
      console.log('Status type:', typeof result.status);
      console.log('Has access_token:', !!result.access_token);
      console.log('Has user:', !!result.user);
      console.log('=====================================');

      if (result.status === 'approved') {
        // Login successful - verifyMFA already handled token storage and dispatch
        console.log('✅ LOGIN APPROVED!');
        console.log('User:', result.user);

        setMfaStatus('approved');
        setMfaMessage('Login successful! Redirecting...');
        clearInterval(pollingInterval.current);
        setSubmittedOtp(null); // Clear stored OTP
        preload('api/menu/dashboard', fetcher);
        // verifyMFA already logged the user in, no need to do anything else
      } else if (result.status === 'denied') {
        // User denied the push or invalid OTP
        console.log('✗ LOGIN DENIED');
        setMfaStatus('denied');
        const isOtpMethod = selectedMethod === 'duo_sms' || selectedMethod === 'email_otp' || selectedMethod === 'twilio_sms' || selectedMethod === 'totp';
        setMfaMessage(isOtpMethod ? 'Invalid verification code.' : 'Authentication denied. Please try again.');
        clearInterval(pollingInterval.current);
        setSubmittedOtp(null); // Clear stored OTP
      } else if (result.status === 'error') {
        // Error occurred
        console.log('✗ ERROR STATUS');
        setMfaStatus('error');
        setMfaMessage(result.message || 'An error occurred. Please try again.');
        clearInterval(pollingInterval.current);
        setSubmittedOtp(null); // Clear stored OTP
      } else {
        // Still pending - show appropriate message based on method
        console.log('⏳ Still pending, status:', result.status);
        const isOtpMethod = selectedMethod === 'duo_sms' || selectedMethod === 'email_otp';
        if (isOtpMethod) {
          setMfaMessage('Verifying your code...');
        } else {
          setMfaMessage('Waiting for approval on your mobile device...');
        }
      }
    } catch (error) {
      console.error('========== MFA POLLING ERROR ==========');
      console.error('Error:', error);
      console.error('Error response:', error.response?.data);
      console.error('=======================================');
      setMfaStatus('error');
      setMfaMessage('An error occurred. Please try again.');
      clearInterval(pollingInterval.current);
      setSubmittedOtp(null); // Clear stored OTP
    }
  };

  // Handle OTP verification
  const handleOtpVerification = async () => {
    try {
      setIsVerifying(true);
      setOtpError('');

      // Validate OTP code
      if (!otpCode || otpCode.trim().length === 0) {
        setOtpError('Please enter the verification code');
        setIsVerifying(false);
        return;
      }

      console.log('========== SUBMITTING OTP ==========');
      console.log('OTP Code:', otpCode);
      console.log('MFA Token:', mfaToken);
      console.log('Selected Method:', selectedMethod);

      // Use verifyMFA from context - it handles token storage and login automatically
      const result = await verifyMFA(mfaToken, otpCode.trim());

      console.log('========== OTP SUBMISSION RESPONSE ==========');
      console.log('Full response:', JSON.stringify(result, null, 2));
      console.log('Status:', result.status);
      console.log('Message:', result.message);
      console.log('==========================================');

      // Check immediate response
      if (result.status === 'approved' || result.status === 'success') {
        // Login successful - verifyMFA already handled token storage and dispatch
        console.log('✅ MFA Verification SUCCESS!');
        console.log('User:', result.user);

        setMfaStatus('approved');
        setMfaMessage('Login successful! Redirecting...');
        preload('api/menu/dashboard', fetcher);
        // verifyMFA already logged the user in, no need to do anything else
      } else if (result.status === 'denied' || result.status === 'invalid' || result.status === 'failed') {
        // Invalid OTP
        setOtpError(result.message || 'Invalid verification code. Please try again.');
        setOtpCode('');
        setOtpBoxes(['', '', '', '', '', '']);
        setIsVerifying(false);
        // Focus first box for retry
        setTimeout(() => otpInputRefs.current[0]?.focus(), 100);
      } else if (result.status === 'pending' || result.status === 'waiting') {
        // OTP submitted successfully, now poll for verification
        console.log('OTP submitted, starting polling...');
        const submittedCode = otpCode.trim();
        setSubmittedOtp(submittedCode); // Store the OTP for polling
        setMfaStatus('pending');
        setMfaMessage('Verifying your code...');

        // Start polling after submitting OTP - pass the OTP code
        setTimeout(() => {
          pollingInterval.current = setInterval(() => {
            pollMFAStatus(mfaToken, submittedCode);
          }, 2000); // Poll every 2 seconds for faster response

          // Do initial poll immediately with OTP
          pollMFAStatus(mfaToken, submittedCode);
        }, 1000);
      } else {
        // Unknown status
        console.error('Unknown status received:', result.status);
        console.error('Full response:', result);
        setOtpError(`Unexpected response status: ${result.status}. Please try again.`);
        setIsVerifying(false);
      }
    } catch (error) {
      console.error('OTP verification error:', error);
      console.error('Error response:', error.response);
      setOtpError(error.response?.data?.detail || error.message || 'Verification failed. Please try again.');
      setIsVerifying(false);
    }
  };

  // Handle OTP box input
  const handleOtpBoxChange = (index, value) => {
    // Only allow hex characters (0-9, A-F)
    if (value && !/^[0-9A-Fa-f]$/.test(value)) {
      return;
    }

    const newBoxes = [...otpBoxes];
    newBoxes[index] = value.toUpperCase();
    setOtpBoxes(newBoxes);
    setOtpError('');

    // Update combined OTP code
    const combinedCode = newBoxes.join('');
    setOtpCode(combinedCode);

    // Auto-focus next box
    if (value && index < 5) {
      otpInputRefs.current[index + 1]?.focus();
    }
  };

  // Handle backspace in OTP boxes
  const handleOtpBoxKeyDown = (index, e) => {
    if (e.key === 'Backspace' && !otpBoxes[index] && index > 0) {
      // Move to previous box on backspace if current is empty
      otpInputRefs.current[index - 1]?.focus();
    } else if (e.key === 'Enter' && otpBoxes.join('').length === 6) {
      // Submit on Enter if all boxes filled
      handleOtpVerification();
    }
  };

  // Handle paste in OTP boxes
  const handleOtpBoxPaste = (e) => {
    e.preventDefault();
    const pastedData = e.clipboardData.getData('text').trim().toUpperCase();

    // Only allow 6 alphanumeric characters (hex)
    if (/^[0-9A-F]{6}$/.test(pastedData)) {
      const newBoxes = pastedData.split('');
      setOtpBoxes(newBoxes);
      setOtpCode(pastedData);
      setOtpError('');
      // Focus last box
      otpInputRefs.current[5]?.focus();
    }
  };

  // Cleanup polling on unmount
  useEffect(() => {
    return () => {
      if (pollingInterval.current) {
        clearInterval(pollingInterval.current);
      }
    };
  }, []);

  // Debug logging
  console.log('Current state - mfaStatus:', mfaStatus, 'mfaToken:', mfaToken ? 'present' : 'null', 'selectedMethod:', selectedMethod);

  return (
    <>
      {mfaStatus === 'otp_input' && mfaToken ? (
        // Show OTP input screen
        <Box sx={{ py: 2 }}>
          <Typography variant="h4" gutterBottom>
            Enter Verification Code
          </Typography>
          <Typography variant="body2" color="text.secondary" sx={{ mb: 3 }}>
            {mfaMessage}
          </Typography>

          <Stack spacing={2}>
            <Stack sx={{ gap: 1 }}>
              <InputLabel>Verification Code</InputLabel>
              <Box
                sx={{
                  display: 'flex',
                  gap: 1,
                  justifyContent: 'center',
                  mb: 1
                }}
              >
                {otpBoxes.map((digit, index) => (
                  <OutlinedInput
                    key={index}
                    inputRef={(el) => (otpInputRefs.current[index] = el)}
                    value={digit}
                    onChange={(e) => handleOtpBoxChange(index, e.target.value)}
                    onKeyDown={(e) => handleOtpBoxKeyDown(index, e)}
                    onPaste={handleOtpBoxPaste}
                    disabled={isVerifying}
                    autoFocus={index === 0}
                    error={Boolean(otpError)}
                    inputProps={{
                      maxLength: 1,
                      style: {
                        textAlign: 'center',
                        fontSize: '1.25rem',
                        fontWeight: 'bold',
                        padding: '8px',
                        width: '32px',
                        height: '32px'
                      }
                    }}
                    sx={{
                      width: '48px',
                      '& input': {
                        padding: '8px'
                      }
                    }}
                  />
                ))}
              </Box>
              {otpError && (
                <FormHelperText error sx={{ textAlign: 'center' }}>{otpError}</FormHelperText>
              )}
            </Stack>

            <AnimateButton>
              <Button
                fullWidth
                size="large"
                variant="contained"
                onClick={handleOtpVerification}
                disabled={isVerifying || otpCode.length !== 6}
              >
                {isVerifying ? (
                  <>
                    <CircularProgress size={20} sx={{ mr: 1 }} color="inherit" />
                    Verifying...
                  </>
                ) : (
                  'Verify Code'
                )}
              </Button>
            </AnimateButton>

            <Button
              variant="text"
              onClick={() => {
                setMfaStatus('selection');
                setSelectedMethod(null);
                setOtpCode('');
                setOtpBoxes(['', '', '', '', '', '']);
                setOtpError('');
                setSubmittedOtp(null);
              }}
              disabled={isVerifying}
              sx={{ mt: 1 }}
            >
              Choose Different Method
            </Button>
          </Stack>
        </Box>
      ) : mfaStatus === 'selection' && mfaToken ? (
        // Show MFA method selection screen
        <Box sx={{ py: 2 }}>
          <Typography variant="h4" gutterBottom>
            Choose Authentication Method
          </Typography>
          <Typography variant="body2" color="text.secondary" sx={{ mb: 3 }}>
            Select how you want to verify your identity
          </Typography>

          <Stack spacing={2}>
            

            {/* Hidden for now - SMS Passcode (Duo) */}
            {/* {availableMfaMethods.includes('duo_sms') && (
              <Button
                fullWidth
                variant="outlined"
                size="large"
                onClick={() => triggerMfaMethod('duo_sms')}
                startIcon={<MessageOutlined />}
                sx={{ justifyContent: 'flex-start', py: 2, textAlign: 'left' }}
              >
                <Box>
                  <Typography variant="subtitle1">SMS Passcode (Duo)</Typography>
                  <Typography variant="caption" color="text.secondary">
                    Get a one-time code via text message (Duo Security)
                  </Typography>
                </Box>
              </Button>
            )} */}

            {availableMfaMethods.includes('twilio_sms') && (
              <Button
                fullWidth
                variant="outlined"
                size="large"
                onClick={() => triggerMfaMethod('twilio_sms')}
                startIcon={<MessageOutlined />}
                sx={{ justifyContent: 'flex-start', py: 2, textAlign: 'left' }}
              >
                <Box>
                  <Typography variant="subtitle1">SMS Verification</Typography>
                  <Typography variant="caption" color="text.secondary">
                    Get a one-time code via text message
                  </Typography>
                </Box>
              </Button>
            )}

            {availableMfaMethods.includes('email_otp') && (
              <Button
                fullWidth
                variant="outlined"
                size="large"
                onClick={() => triggerMfaMethod('email_otp')}
                startIcon={<MailOutlined />}
                sx={{ justifyContent: 'flex-start', py: 2, textAlign: 'left' }}
              >
                <Box>
                  <Typography variant="subtitle1">Email Verification Code</Typography>
                  <Typography variant="caption" color="text.secondary">
                    Get a one-time code via email
                  </Typography>
                </Box>
              </Button>
            )}

            {availableMfaMethods.includes('totp') && (
              <Button
                fullWidth
                variant="outlined"
                size="large"
                onClick={() => triggerMfaMethod('totp')}
                startIcon={<SafetyOutlined />}
                sx={{ justifyContent: 'flex-start', py: 2, textAlign: 'left' }}
              >
                <Box>
                  <Typography variant="subtitle1">Authenticator App</Typography>
                  <Typography variant="caption" color="text.secondary">
                    Use your authenticator app 
                  </Typography>
                </Box>
              </Button>
            )}

            {availableMfaMethods.includes('duo_push') && (
              <Button
                fullWidth
                variant="outlined"
                size="large"
                onClick={() => triggerMfaMethod('duo_push')}
                startIcon={<MobileOutlined />}
                sx={{ justifyContent: 'flex-start', py: 2, textAlign: 'left' }}
              >
                <Box>
                  <Typography variant="subtitle1">Duo Push Notification</Typography>
                  <Typography variant="caption" color="text.secondary">
                    Get a push notification on your Duo Mobile app
                  </Typography>
                </Box>
              </Button>
            )}

            {availableMfaMethods.includes('duo_phone') && (
              <Button
                fullWidth
                variant="outlined"
                size="large"
                onClick={() => triggerMfaMethod('duo_phone')}
                startIcon={<PhoneOutlined />}
                sx={{ justifyContent: 'flex-start', py: 2, textAlign: 'left' }}
              >
                <Box>
                  <Typography variant="subtitle1">Phone Call</Typography>
                  <Typography variant="caption" color="text.secondary">
                    Receive an automated phone call
                  </Typography>
                </Box>
              </Button>
            )}
          </Stack>

          <Button
            variant="text"
            onClick={() => {
              setMfaStatus(null);
              setMfaToken(null);
              setAvailableMfaMethods([]);
              setSubmittedOtp(null);
              setOtpCode('');
              setOtpBoxes(['', '', '', '', '', '']);
              setOtpError('');
            }}
            sx={{ mt: 3, display: 'block', mx: 'auto' }}
          >
            Back to Login
          </Button>
        </Box>
      ) : mfaStatus === 'pending' && mfaToken ? (
        // Show authentication waiting screen
        <Box sx={{ textAlign: 'center', py: 4 }}>
          {selectedMethod === 'duo_push' && (
            <MobileOutlined style={{ fontSize: 64, color: '#1890ff', marginBottom: 16 }} />
          )}
          {selectedMethod === 'duo_phone' && (
            <PhoneOutlined style={{ fontSize: 64, color: '#1890ff', marginBottom: 16 }} />
          )}
          {selectedMethod === 'duo_sms' && (
            <MessageOutlined style={{ fontSize: 64, color: '#1890ff', marginBottom: 16 }} />
          )}
          {selectedMethod === 'twilio_sms' && (
            <MessageOutlined style={{ fontSize: 64, color: '#1890ff', marginBottom: 16 }} />
          )}
          {selectedMethod === 'email_otp' && (
            <MailOutlined style={{ fontSize: 64, color: '#1890ff', marginBottom: 16 }} />
          )}
          {selectedMethod === 'totp' && (
            <SafetyOutlined style={{ fontSize: 64, color: '#1890ff', marginBottom: 16 }} />
          )}
          {!selectedMethod && (
            <MobileOutlined style={{ fontSize: 64, color: '#1890ff', marginBottom: 16 }} />
          )}
          <Typography variant="h3" gutterBottom>
            {selectedMethod === 'duo_push'
              ? 'Duo Push Sent'
              : selectedMethod === 'duo_phone'
                ? 'Calling Your Phone'
                : (selectedMethod === 'duo_sms' || selectedMethod === 'email_otp' || selectedMethod === 'totp')
                  ? 'Verifying Code'
                  : 'Authentication Requested'}
          </Typography>
          <Typography variant="body1" color="text.secondary" sx={{ mb: 3 }}>
            {mfaMessage}
          </Typography>
          <CircularProgress size={40} />
          <Button
            variant="text"
            onClick={() => {
              clearInterval(pollingInterval.current);
              setMfaStatus('selection');
              setSelectedMethod(null);
              setSubmittedOtp(null);
            }}
            sx={{ mt: 3, display: 'block', mx: 'auto' }}
          >
            Choose Different Method
          </Button>
        </Box>
      ) : mfaStatus === 'denied' || mfaStatus === 'error' ? (
        // Show error/denied state
        <Box>
          <Alert severity="error" sx={{ mb: 2 }}>
            {mfaMessage}
          </Alert>
          <Stack spacing={2}>
            <Button
              fullWidth
              variant="contained"
              onClick={() => {
                setMfaStatus('selection');
                setMfaMessage('');
                setSubmittedOtp(null);
                setOtpCode('');
                setOtpBoxes(['', '', '', '', '', '']);
                setOtpError('');
                setSelectedMethod(null);
              }}
            >
              Choose Different Method
            </Button>
            <Button
              fullWidth
              variant="outlined"
              onClick={() => {
                setMfaStatus(null);
                setMfaToken(null);
                setMfaMessage('');
                setSubmittedOtp(null);
                setOtpCode('');
                setOtpBoxes(['', '', '', '', '', '']);
                setOtpError('');
                setSelectedMethod(null);
              }}
            >
              Back to Login
            </Button>
          </Stack>
        </Box>
      ) : (
        // Show normal login form
        <Formik
          initialValues={{
            email: '',
            password: '',
            submit: null
          }}
          validationSchema={Yup.object().shape({
            email: Yup.string().email('Must be a valid email').max(255).required('Email is required'),
            password: Yup.string()
              .required('Password is required')
              .test('no-leading-trailing-whitespace', 'Password cannot start or end with spaces', (value) => value === value.trim())
          })}
          onSubmit={async (values, { setErrors, setStatus, setSubmitting }) => {
            try {
              // Execute reCAPTCHA v3 before login
              let recaptchaToken = null;
              if (recaptchaSiteKey && recaptchaRef.current) {
                try {
                  recaptchaToken = await recaptchaRef.current.executeAsync();
                  recaptchaRef.current.reset(); // Reset for next submission
                } catch (recaptchaError) {
                  console.error('reCAPTCHA execution failed:', recaptchaError);
                  setErrors({ submit: 'Security verification failed. Please try again.' });
                  setSubmitting(false);
                  return;
                }
              }

              const trimmedEmail = values.email.trim();
              const result = await login(trimmedEmail, values.password, recaptchaToken);
              console.log('Login result:', result);

              // Check if MFA is required
              if (result.requires_mfa && result.mfa_token) {
                setMfaToken(result.mfa_token);
                console.log('MFA required, token:', result.mfa_token);
                console.log('MFA method:', result.mfa_method);
                console.log('Available methods:', result.available_mfa_methods);

                // Check if user needs to select MFA method
                if (result.mfa_method === 'selection' && result.available_mfa_methods && result.available_mfa_methods.length > 0) {
                  // Show MFA selection screen
                  console.log('Showing MFA selection screen');
                  setMfaStatus('selection');
                  setAvailableMfaMethods(result.available_mfa_methods);
                  setMfaMessage('Please select an authentication method to continue');
                  // Do NOT start polling yet - wait for user to select method
                } else {
                  // Auto-send (backward compatibility for non-selection flows)
                  console.warn('No selection - auto-triggering MFA (this should not happen with new flow)');
                  setMfaStatus('pending');
                  setMfaMessage('Sending authentication request...');

                  // Start polling for MFA status every 3 seconds
                  pollingInterval.current = setInterval(() => {
                    pollMFAStatus(result.mfa_token);
                  }, 3000);

                  // Do initial poll immediately
                  setTimeout(() => pollMFAStatus(result.mfa_token), 1000);
                }
              } else {
                // Normal login (no MFA)
                setStatus({ success: true });
                preload('api/menu/dashboard', fetcher);
              }

              setSubmitting(false);
            } catch (err) {
              console.error('Login error:', err);
              setStatus({ success: false });

              // Extract error message from axios error response
              let errorMessage = 'An error occurred during login';
              if (err.response?.data?.detail) {
                errorMessage = err.response.data.detail;
              } else if (err.response?.data?.message) {
                errorMessage = err.response.data.message;
              } else if (err.message) {
                errorMessage = err.message;
              }

              setErrors({ submit: errorMessage });
              setSubmitting(false);
            }
          }}
        >
        {({ errors, handleBlur, handleChange, handleSubmit, isSubmitting, touched, values }) => (
          <form noValidate onSubmit={handleSubmit}>
            <Grid container spacing={3}>
              <Grid size={12}>
                <Stack sx={{ gap: 1 }}>
                  <InputLabel htmlFor="email-login">Email Address</InputLabel>
                  <OutlinedInput
                    id="email-login"
                    type="email"
                    value={values.email}
                    name="email"
                    onBlur={handleBlur}
                    onChange={handleChange}
                    placeholder="Enter email address"
                    fullWidth
                    error={Boolean(touched.email && errors.email)}
                  />
                </Stack>
                {touched.email && errors.email && (
                  <FormHelperText error id="standard-weight-helper-text-email-login">
                    {errors.email}
                  </FormHelperText>
                )}
              </Grid>
              <Grid size={12}>
                <Stack sx={{ gap: 1 }}>
                  <InputLabel htmlFor="password-login">Password</InputLabel>
                  <OutlinedInput
                    fullWidth
                    error={Boolean(touched.password && errors.password)}
                    id="-password-login"
                    type={showPassword ? 'text' : 'password'}
                    value={values.password}
                    name="password"
                    onBlur={handleBlur}
                    onChange={handleChange}
                    endAdornment={
                      <InputAdornment position="end">
                        <IconButton
                          aria-label="toggle password visibility"
                          onClick={handleClickShowPassword}
                          onMouseDown={handleMouseDownPassword}
                          edge="end"
                          color="secondary"
                        >
                          {showPassword ? <EyeOutlined /> : <EyeInvisibleOutlined />}
                        </IconButton>
                      </InputAdornment>
                    }
                    placeholder="Enter password"
                  />
                </Stack>
                {touched.password && errors.password && (
                  <FormHelperText error id="standard-weight-helper-text-password-login">
                    {errors.password}
                  </FormHelperText>
                )}
              </Grid>
              <Grid sx={{ mt: -1 }} size={12}>
                <Stack direction="row" sx={{ gap: 2, alignItems: 'baseline', justifyContent: 'space-between' }}>
                  <FormControlLabel
                    control={
                      <Checkbox
                        checked={checked}
                        onChange={(event) => setChecked(event.target.checked)}
                        name="checked"
                        color="primary"
                        size="small"
                      />
                    }
                    label={<Typography variant="h6">Keep me sign in</Typography>}
                  />
                  <Link
                    variant="h6"
                    component={RouterLink}
                    to={isDemo ? '/auth/forgot-password' : auth ? `/${auth}/forgot-password?auth=jwt` : '/forgot-password'}
                    color="text.primary"
                  >
                    Forgot Password?
                  </Link>
                </Stack>
              </Grid>
              {errors.submit && (
                <Grid size={12}>
                  <FormHelperText error>{errors.submit}</FormHelperText>
                </Grid>
              )}
              <Grid size={12}>
                <AnimateButton>
                  <Button disableElevation disabled={isSubmitting} fullWidth size="large" type="submit" variant="contained" color="primary">
                    Login
                  </Button>
                </AnimateButton>
              </Grid>
            </Grid>
            {recaptchaSiteKey && (
              <ReCAPTCHA
                ref={recaptchaRef}
                size="invisible"
                sitekey={recaptchaSiteKey}
                badge="bottomright"
              />
            )}
          </form>
          )}
        </Formik>
      )}
    </>
  );
}

AuthLogin.propTypes = { isDemo: PropTypes.bool };
