import PropTypes from 'prop-types';
import React, { useEffect, useRef } from 'react';
import { Link as RouterLink, useSearchParams } from 'react-router-dom';

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

// ============================|| JWT - LOGIN ||============================ //

export default function AuthLogin({ isDemo = false }) {
  const [checked, setChecked] = React.useState(false);
  const [mfaStatus, setMfaStatus] = React.useState(null); // 'pending', 'approved', 'denied', 'error', 'selection'
  const [mfaToken, setMfaToken] = React.useState(null);
  const [mfaMessage, setMfaMessage] = React.useState('');
  const [availableMfaMethods, setAvailableMfaMethods] = React.useState([]);
  const [selectedMethod, setSelectedMethod] = React.useState(null);
  const pollingInterval = useRef(null);

  const { login, verifyMFA } = useAuth();

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

      // IMMEDIATELY show the waiting screen
      setSelectedMethod(method);
      setMfaStatus('pending');
      setMfaMessage('Sending authentication request...');

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

      // Update message with server response
      console.log('MFA triggered successfully');
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

    } catch (error) {
      console.error('MFA trigger error:', error);
      setMfaStatus('error');
      setMfaMessage(error.message || 'Failed to send authentication request. Please try again.');
    }
  };

  // Poll MFA status
  const pollMFAStatus = async (token) => {
    try {
      console.log('Polling MFA status...');
      const result = await verifyMFA(token);
      console.log('Poll result:', result);

      if (result.status === 'approved') {
        // Login successful
        setMfaStatus('approved');
        setMfaMessage('Login successful! Redirecting...');
        clearInterval(pollingInterval.current);
        preload('api/menu/dashboard', fetcher);
      } else if (result.status === 'denied') {
        // User denied the push
        setMfaStatus('denied');
        setMfaMessage('Authentication denied. Please try again.');
        clearInterval(pollingInterval.current);
      } else if (result.status === 'error') {
        // Error occurred
        setMfaStatus('error');
        setMfaMessage(result.message || 'An error occurred. Please try again.');
        clearInterval(pollingInterval.current);
      } else {
        // Still pending
        setMfaMessage('Waiting for approval on your mobile device...');
      }
    } catch (error) {
      console.error('MFA polling error:', error);
      setMfaStatus('error');
      setMfaMessage('An error occurred. Please try again.');
      clearInterval(pollingInterval.current);
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
      {mfaStatus === 'selection' && mfaToken ? (
        // Show MFA method selection screen
        <Box sx={{ py: 2 }}>
          <Typography variant="h4" gutterBottom>
            Choose Authentication Method
          </Typography>
          <Typography variant="body2" color="text.secondary" sx={{ mb: 3 }}>
            Select how you want to verify your identity
          </Typography>

          <Stack spacing={2}>
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
                startIcon={<MobileOutlined />}
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

            {availableMfaMethods.includes('duo_sms') && (
              <Button
                fullWidth
                variant="outlined"
                size="large"
                onClick={() => triggerMfaMethod('duo_sms')}
                startIcon={<MobileOutlined />}
                sx={{ justifyContent: 'flex-start', py: 2, textAlign: 'left' }}
              >
                <Box>
                  <Typography variant="subtitle1">SMS Passcode</Typography>
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
                startIcon={<MobileOutlined />}
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
          </Stack>

          <Button
            variant="text"
            onClick={() => {
              setMfaStatus(null);
              setMfaToken(null);
              setAvailableMfaMethods([]);
            }}
            sx={{ mt: 3, display: 'block', mx: 'auto' }}
          >
            Back to Login
          </Button>
        </Box>
      ) : mfaStatus === 'pending' && mfaToken ? (
        // Show authentication waiting screen
        <Box sx={{ textAlign: 'center', py: 4 }}>
          <MobileOutlined style={{ fontSize: 64, color: '#1890ff', marginBottom: 16 }} />
          <Typography variant="h3" gutterBottom>
            {selectedMethod === 'duo_push' ? 'Duo Push Sent' : 'Authentication Requested'}
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
          <Button
            fullWidth
            variant="contained"
            onClick={() => {
              setMfaStatus(null);
              setMfaToken(null);
              setMfaMessage('');
            }}
          >
            Try Again
          </Button>
        </Box>
      ) : (
        // Show normal login form
        <Formik
          initialValues={{
            email: 'niteesh.kl@jillellagroup.com',
            password: 'SecurePass123!',
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
              const trimmedEmail = values.email.trim();
              const result = await login(trimmedEmail, values.password);
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
          </form>
          )}
        </Formik>
      )}
    </>
  );
}

AuthLogin.propTypes = { isDemo: PropTypes.bool };
