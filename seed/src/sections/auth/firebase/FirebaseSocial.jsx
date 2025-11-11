import useMediaQuery from '@mui/material/useMediaQuery';
import Button from '@mui/material/Button';
import CardMedia from '@mui/material/CardMedia';
import Stack from '@mui/material/Stack';

// project imports
import useAuth from 'hooks/useAuth';

// assets
import Google from 'assets/images/icons/google.svg';
import Microsoft from 'assets/images/icons/microsoft.svg';
import Apple from 'assets/images/icons/apple.svg';

// ==============================|| FIREBASE - SOCIAL BUTTON ||============================== //

export default function FirebaseSocial() {
  const downSM = useMediaQuery((theme) => theme.breakpoints.down('sm'));

  // @ts-ignore
  const { firebaseGoogleSignIn } = useAuth();

  const googleHandler = async () => {
    try {
      // Redirect to backend OAuth endpoint
      const backendUrl = import.meta.env.VITE_APP_API_URL || 'http://localhost:3010/';
      window.location.href = `${backendUrl}api/v1/oauth/google/authorize`;
    } catch (err) {
      console.error(err);
    }
  };

  const microsoftHandler = async () => {
    try {
      // Redirect to backend OAuth endpoint
      const backendUrl = import.meta.env.VITE_APP_API_URL || 'http://localhost:3010/';
      window.location.href = `${backendUrl}api/v1/oauth/microsoft/authorize`;
    } catch (err) {
      console.error(err);
    }
  };

  const appleHandler = async () => {
    // Apple OAuth requires Apple Developer account
    alert('Apple Login - Coming Soon\n\nApple Sign-In is currently under development.\n\nNote: Apple Sign-In requires an Apple Developer account ($99/year) to configure the necessary credentials and services.\n\nPlease use Google or Microsoft to sign in.');
  };

  return (
    <Stack
      direction="row"
      sx={{ gap: { xs: 1, sm: 2 }, justifyContent: { xs: 'space-around', sm: 'space-between' }, '& .MuiButton-startIcon': { mr: { xs: 0, sm: 1 } } }}
    >
      <Button
        variant="outlined"
        color="secondary"
        fullWidth={!downSM}
        startIcon={<CardMedia component="img" src={Google} alt="Google" sx={{ width: 16, height: 16 }} />}
        onClick={googleHandler}
      >
        {!downSM && 'Google'}
      </Button>
      <Button
        variant="outlined"
        color="secondary"
        fullWidth={!downSM}
        startIcon={<CardMedia component="img" src={Microsoft} alt="Microsoft" sx={{ width: 16, height: 16 }} />}
        onClick={microsoftHandler}
      >
        {!downSM && 'Microsoft'}
      </Button>
      <Button
        variant="outlined"
        color="secondary"
        fullWidth={!downSM}
        startIcon={<CardMedia component="img" src={Apple} alt="Apple" sx={{ width: 16, height: 16 }} />}
        onClick={appleHandler}
      >
        {!downSM && 'Apple'}
      </Button>
    </Stack>
  );
}
