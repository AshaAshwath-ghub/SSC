import { useState, useEffect } from 'react';
import {
  Box,
  Button,
  Card,
  CardContent,
  CardHeader,
  Divider,
  Typography,
  Alert,
  Dialog,
  DialogTitle,
  DialogContent,
  DialogActions,
  List,
  ListItem,
  ListItemIcon,
  ListItemText,
  Chip,
  Stack
} from '@mui/material';
import CheckCircleOutlined from '@ant-design/icons/CheckCircleOutlined';
import CloseCircleOutlined from '@ant-design/icons/CloseCircleOutlined';
import PlusOutlined from '@ant-design/icons/PlusOutlined';
import MainCard from 'components/MainCard';
import AuthTOTPSetup from 'sections/auth/jwt/AuthTOTPSetup';
import useAuth from 'hooks/useAuth';
import axios from 'utils/axios';

/**
 * TOTP Settings Page
 *
 * Allows users to manage their TOTP (Time-based One-Time Password) authentication.
 * Users can:
 * - Set up TOTP authenticator app
 * - View TOTP status
 * - Disable TOTP
 * - Regenerate backup codes (future enhancement)
 */
const TOTPSettings = () => {
  const { user } = useAuth();
  const [totpEnabled, setTotpEnabled] = useState(false);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);
  const [successMessage, setSuccessMessage] = useState(null);
  const [showSetupDialog, setShowSetupDialog] = useState(false);
  const [showDisableDialog, setShowDisableDialog] = useState(false);

  /**
   * Check if user has TOTP enabled
   * This would typically call an API endpoint to check enrollment status
   */
  useEffect(() => {
    checkTOTPStatus();
  }, []);

  const checkTOTPStatus = async () => {
    try {
      // In a real implementation, you would call an API endpoint like:
      // const response = await axios.get('/api/v1/auth/mfa/totp/status');
      // setTotpEnabled(response.data.is_enabled);

      // For now, we'll simulate this check
      // You'll need to implement the backend endpoint
      setTotpEnabled(false);
    } catch (err) {
      console.error('Error checking TOTP status:', err);
    }
  };

  /**
   * Handle TOTP setup completion
   */
  const handleSetupComplete = (data) => {
    setTotpEnabled(true);
    setShowSetupDialog(false);
    setSuccessMessage('TOTP authenticator has been successfully configured!');
    setTimeout(() => setSuccessMessage(null), 5000);
  };

  /**
   * Handle TOTP disable
   */
  const handleDisableTOTP = async () => {
    setLoading(true);
    setError(null);

    try {
      // Call API to disable TOTP
      // await axios.post('/api/v1/auth/mfa/totp/disable');

      setTotpEnabled(false);
      setShowDisableDialog(false);
      setSuccessMessage('TOTP authenticator has been disabled.');
      setTimeout(() => setSuccessMessage(null), 5000);
    } catch (err) {
      setError(err.response?.data?.detail || 'Failed to disable TOTP. Please try again.');
    } finally {
      setLoading(false);
    }
  };

  return (
    <MainCard title="Two-Factor Authentication Settings">
      <Stack spacing={3}>
        {/* Success Message */}
        {successMessage && (
          <Alert severity="success" onClose={() => setSuccessMessage(null)}>
            {successMessage}
          </Alert>
        )}

        {/* Error Message */}
        {error && (
          <Alert severity="error" onClose={() => setError(null)}>
            {error}
          </Alert>
        )}

        {/* TOTP Status Card */}
        <Card variant="outlined">
          <CardHeader
            title="Authenticator App"
            subheader="Use an authenticator app to generate verification codes"
            action={
              totpEnabled ? (
                <Chip label="Enabled" color="success" icon={<CheckCircleOutlined />} />
              ) : (
                <Chip label="Not Enabled" icon={<CloseCircleOutlined />} />
              )
            }
          />
          <Divider />
          <CardContent>
            <Typography variant="body2" color="text.secondary" paragraph>
              Two-factor authentication adds an extra layer of security to your account by requiring a verification code from an
              authenticator app in addition to your password when you sign in.
            </Typography>

            {totpEnabled ? (
              <Box>
                <Alert severity="success" icon={<CheckCircleOutlined />} sx={{ mb: 2 }}>
                  Your account is protected with authenticator app verification.
                </Alert>
                <Typography variant="body2" paragraph>
                  Compatible Apps:
                </Typography>
                <List dense>
                  <ListItem>• Google Authenticator</ListItem>
                  <ListItem>• Microsoft Authenticator</ListItem>
                  <ListItem>• Authy</ListItem>
                  <ListItem>• 1Password</ListItem>
                </List>
                <Button variant="outlined" color="error" onClick={() => setShowDisableDialog(true)} sx={{ mt: 2 }}>
                  Disable Authenticator App
                </Button>
              </Box>
            ) : (
              <Box>
                <Alert severity="info" sx={{ mb: 2 }}>
                  Authenticator apps are more secure than SMS. We recommend using Google Authenticator, Microsoft Authenticator, or
                  Authy.
                </Alert>
                <Button variant="contained" startIcon={<PlusOutlined />} onClick={() => setShowSetupDialog(true)}>
                  Set Up Authenticator App
                </Button>
              </Box>
            )}
          </CardContent>
        </Card>

        {/* Additional Security Information */}
        <Card variant="outlined">
          <CardHeader title="Security Recommendations" />
          <Divider />
          <CardContent>
            <List>
              <ListItem>
                <ListItemIcon>
                  <CheckCircleOutlined style={{ color: '#52c41a' }} />
                </ListItemIcon>
                <ListItemText
                  primary="Save your backup codes"
                  secondary="Store backup codes in a safe place to access your account if you lose your device"
                />
              </ListItem>
              <ListItem>
                <ListItemIcon>
                  <CheckCircleOutlined style={{ color: '#52c41a' }} />
                </ListItemIcon>
                <ListItemText
                  primary="Keep your device time synced"
                  secondary="Ensure your device's clock is set to automatic for codes to work properly"
                />
              </ListItem>
              <ListItem>
                <ListItemIcon>
                  <CheckCircleOutlined style={{ color: '#52c41a' }} />
                </ListItemIcon>
                <ListItemText
                  primary="Use multiple authentication methods"
                  secondary="Set up multiple MFA methods (Email, SMS, Authenticator) for account recovery"
                />
              </ListItem>
            </List>
          </CardContent>
        </Card>
      </Stack>

      {/* Setup Dialog */}
      <Dialog open={showSetupDialog} onClose={() => setShowSetupDialog(false)} maxWidth="sm" fullWidth>
        <DialogTitle>Set Up Authenticator App</DialogTitle>
        <DialogContent>
          <AuthTOTPSetup
            userEmail={user?.email || ''}
            onSetupComplete={handleSetupComplete}
            onCancel={() => setShowSetupDialog(false)}
          />
        </DialogContent>
      </Dialog>

      {/* Disable Confirmation Dialog */}
      <Dialog open={showDisableDialog} onClose={() => setShowDisableDialog(false)} maxWidth="xs" fullWidth>
        <DialogTitle>Disable Authenticator App?</DialogTitle>
        <DialogContent>
          <Typography variant="body2" color="text.secondary">
            Are you sure you want to disable authenticator app verification? This will make your account less secure.
          </Typography>
          <Alert severity="warning" sx={{ mt: 2 }}>
            Make sure you have at least one other authentication method enabled before disabling this one.
          </Alert>
        </DialogContent>
        <DialogActions>
          <Button onClick={() => setShowDisableDialog(false)} disabled={loading}>
            Cancel
          </Button>
          <Button onClick={handleDisableTOTP} color="error" variant="contained" disabled={loading}>
            {loading ? 'Disabling...' : 'Disable'}
          </Button>
        </DialogActions>
      </Dialog>
    </MainCard>
  );
};

export default TOTPSettings;
