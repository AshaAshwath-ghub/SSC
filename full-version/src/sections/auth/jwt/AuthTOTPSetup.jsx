import { useState } from 'react';
import PropTypes from 'prop-types';
import {
  Box,
  Button,
  TextField,
  Typography,
  Alert,
  Paper,
  Stack,
  Divider,
  List,
  ListItem,
  ListItemIcon,
  ListItemText,
  Chip,
  IconButton,
  Tooltip
} from '@mui/material';
import CopyOutlined from '@ant-design/icons/CopyOutlined';
import CheckCircleOutlined from '@ant-design/icons/CheckCircleOutlined';
import DownloadOutlined from '@ant-design/icons/DownloadOutlined';
import axios from 'utils/axios';

/**
 * TOTP Setup Component
 *
 * Allows users to set up TOTP (Time-based One-Time Password) authentication
 * using authenticator apps like Google Authenticator, Authy, Microsoft Authenticator, etc.
 *
 * Flow:
 * 1. User initiates setup
 * 2. Backend generates secret and QR code
 * 3. User scans QR code with authenticator app
 * 4. User enters first code to verify
 * 5. Backend saves enrollment and provides backup codes
 */
const AuthTOTPSetup = ({ userEmail, onSetupComplete, onCancel }) => {
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);
  const [setupData, setSetupData] = useState(null);
  const [verificationCode, setVerificationCode] = useState('');
  const [secretCopied, setSecretCopied] = useState(false);
  const [backupCodesCopied, setBackupCodesCopied] = useState(false);

  /**
   * Step 1: Initialize TOTP setup
   * Calls backend to generate secret and QR code
   */
  const handleInitiateSetup = async () => {
    setLoading(true);
    setError(null);

    try {
      console.log('Initiating TOTP setup for:', userEmail);
      const response = await axios.post('/api/v1/auth/mfa/totp/setup', {
        user_email: userEmail
      });

      console.log('TOTP setup response:', response.data);
      setSetupData(response.data);
      setLoading(false);
    } catch (err) {
      console.error('TOTP setup error:', err);
      console.error('Error response:', err.response);
      console.error('Error details:', err.response?.data);

      let errorMessage = 'Failed to initiate TOTP setup. Please try again.';
      if (err.response?.data?.detail) {
        errorMessage = err.response.data.detail;
      } else if (err.message) {
        errorMessage = `Error: ${err.message}`;
      }

      setError(errorMessage);
      setLoading(false);
    }
  };

  /**
   * Step 2: Verify TOTP code and complete setup
   * User enters code from authenticator app to confirm it works
   */
  const handleVerifyCode = async () => {
    if (!verificationCode || verificationCode.length !== 6) {
      setError('Please enter a valid 6-digit code');
      return;
    }

    setLoading(true);
    setError(null);

    try {
      const response = await axios.post('/api/v1/auth/mfa/totp/verify-setup', {
        secret: setupData.secret,
        otp_code: verificationCode
      });

      // Setup successful
      if (response.data.status === 'success') {
        // Show success message and allow user to download backup codes
        // Then call onSetupComplete
        setTimeout(() => {
          if (onSetupComplete) {
            onSetupComplete(response.data);
          }
        }, 2000);
      } else {
        setError('Verification failed. Please try again.');
      }

      setLoading(false);
    } catch (err) {
      setError(err.response?.data?.detail || 'Invalid verification code. Please try again.');
      setLoading(false);
    }
  };

  /**
   * Copy secret key to clipboard
   */
  const handleCopySecret = () => {
    navigator.clipboard.writeText(setupData.secret);
    setSecretCopied(true);
    setTimeout(() => setSecretCopied(false), 2000);
  };

  /**
   * Copy backup codes to clipboard
   */
  const handleCopyBackupCodes = () => {
    const codes = setupData.backup_codes.join('\n');
    navigator.clipboard.writeText(codes);
    setBackupCodesCopied(true);
    setTimeout(() => setBackupCodesCopied(false), 2000);
  };

  /**
   * Download backup codes as text file
   */
  const handleDownloadBackupCodes = () => {
    const codes = setupData.backup_codes.join('\n');
    const blob = new Blob([codes], { type: 'text/plain' });
    const url = URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = `totp-backup-codes-${new Date().toISOString().split('T')[0]}.txt`;
    document.body.appendChild(a);
    a.click();
    document.body.removeChild(a);
    URL.revokeObjectURL(url);
  };

  // If setup not initiated, show initiate button
  if (!setupData) {
    return (
      <Box>
        <Typography variant="h5" gutterBottom>
          Set Up Authenticator App
        </Typography>
        <Typography variant="body2" color="text.secondary" sx={{ mb: 3 }}>
          Add an extra layer of security to your account by setting up two-factor authentication with an authenticator app.
        </Typography>

        {error && (
          <Alert severity="error" sx={{ mb: 2 }}>
            {error}
          </Alert>
        )}

        <Alert severity="info" sx={{ mb: 3 }}>
          <Typography variant="subtitle2" gutterBottom>
            You'll need an authenticator app such as:
          </Typography>
          <List dense>
            <ListItem>• Google Authenticator (iOS/Android)</ListItem>
            <ListItem>• Microsoft Authenticator (iOS/Android)</ListItem>
            <ListItem>• Authy (iOS/Android/Desktop)</ListItem>
            <ListItem>• 1Password (iOS/Android/Desktop)</ListItem>
          </List>
        </Alert>

        <Stack direction="row" spacing={2}>
          <Button variant="contained" onClick={handleInitiateSetup} disabled={loading} fullWidth>
            {loading ? 'Setting Up...' : 'Begin Setup'}
          </Button>
          {onCancel && (
            <Button variant="outlined" onClick={onCancel} disabled={loading} fullWidth>
              Cancel
            </Button>
          )}
        </Stack>
      </Box>
    );
  }

  // Show QR code and verification
  return (
    <Box>
      <Typography variant="h5" gutterBottom>
        Scan QR Code
      </Typography>

      {error && (
        <Alert severity="error" sx={{ mb: 2 }}>
          {error}
        </Alert>
      )}

      <Paper variant="outlined" sx={{ p: 3, mb: 3 }}>
        <Stack spacing={3}>
          {/* Step 1: Scan QR Code */}
          <Box>
            <Typography variant="subtitle1" gutterBottom fontWeight="bold">
              Step 1: Scan with your authenticator app
            </Typography>
            <Box sx={{ display: 'flex', justifyContent: 'center', my: 2 }}>
              <img src={setupData.qr_code} alt="TOTP QR Code" style={{ maxWidth: '256px', height: 'auto' }} />
            </Box>
            <Typography variant="body2" color="text.secondary" align="center">
              Scan this QR code with your authenticator app
            </Typography>
          </Box>

          <Divider />

          {/* Manual Entry Option */}
          <Box>
            <Typography variant="subtitle2" gutterBottom>
              Can't scan the code?
            </Typography>
            <Typography variant="body2" color="text.secondary" gutterBottom>
              Enter this key manually in your authenticator app:
            </Typography>
            <Box sx={{ display: 'flex', alignItems: 'center', gap: 1, mt: 1 }}>
              <Chip label={setupData.secret} sx={{ fontFamily: 'monospace', flex: 1 }} />
              <Tooltip title={secretCopied ? 'Copied!' : 'Copy to clipboard'}>
                <IconButton onClick={handleCopySecret} size="small" color={secretCopied ? 'success' : 'default'}>
                  {secretCopied ? <CheckCircleOutlined /> : <CopyOutlined />}
                </IconButton>
              </Tooltip>
            </Box>
            <Typography variant="caption" color="text.secondary" sx={{ mt: 1, display: 'block' }}>
              Account: {userEmail} • Issuer: {setupData.issuer_name}
            </Typography>
          </Box>

          <Divider />

          {/* Step 2: Verify Code */}
          <Box>
            <Typography variant="subtitle1" gutterBottom fontWeight="bold">
              Step 2: Enter verification code
            </Typography>
            <Typography variant="body2" color="text.secondary" gutterBottom>
              Enter the 6-digit code shown in your authenticator app to complete setup
            </Typography>
            <TextField
              fullWidth
              label="6-Digit Code"
              value={verificationCode}
              onChange={(e) => setVerificationCode(e.target.value.replace(/\D/g, '').slice(0, 6))}
              placeholder="000000"
              inputProps={{ maxLength: 6, style: { letterSpacing: '0.5em', fontSize: '1.5rem', textAlign: 'center' } }}
              sx={{ my: 2 }}
              autoFocus
            />
            <Button variant="contained" onClick={handleVerifyCode} disabled={loading || verificationCode.length !== 6} fullWidth>
              {loading ? 'Verifying...' : 'Verify and Complete Setup'}
            </Button>
          </Box>

          <Divider />

          {/* Backup Codes */}
          <Box>
            <Typography variant="subtitle1" gutterBottom fontWeight="bold">
              Step 3: Save backup codes
            </Typography>
            <Alert severity="warning" sx={{ mb: 2 }}>
              <Typography variant="body2" fontWeight="bold">
                IMPORTANT: Save these backup codes in a safe place!
              </Typography>
              <Typography variant="body2">
                You can use these codes to access your account if you lose your device. Each code can only be used once.
              </Typography>
            </Alert>
            <Paper variant="outlined" sx={{ p: 2, bgcolor: 'grey.50', fontFamily: 'monospace', fontSize: '0.875rem' }}>
              {setupData.backup_codes.map((code, index) => (
                <Box key={index}>{code}</Box>
              ))}
            </Paper>
            <Stack direction="row" spacing={1} sx={{ mt: 2 }}>
              <Button
                variant="outlined"
                startIcon={backupCodesCopied ? <CheckCircleOutlined /> : <CopyOutlined />}
                onClick={handleCopyBackupCodes}
                fullWidth
              >
                {backupCodesCopied ? 'Copied!' : 'Copy Codes'}
              </Button>
              <Button variant="outlined" startIcon={<DownloadOutlined />} onClick={handleDownloadBackupCodes} fullWidth>
                Download
              </Button>
            </Stack>
          </Box>
        </Stack>
      </Paper>

      {onCancel && (
        <Button variant="text" onClick={onCancel} disabled={loading} fullWidth>
          Cancel Setup
        </Button>
      )}
    </Box>
  );
};

AuthTOTPSetup.propTypes = {
  userEmail: PropTypes.string.isRequired,
  onSetupComplete: PropTypes.func,
  onCancel: PropTypes.func
};

export default AuthTOTPSetup;
