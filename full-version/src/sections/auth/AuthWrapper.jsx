import PropTypes from 'prop-types';
import { useSearchParams } from 'react-router-dom';

// material-ui
import Grid from '@mui/material/Grid';
import Typography from '@mui/material/Typography';
import Divider from '@mui/material/Divider';
import Box from '@mui/material/Box';

// project imports
import AuthFooter from 'components/cards/AuthFooter';
import Logo from 'components/logo';
import AuthCard from './AuthCard';
import LoginProvider from './LoginProvider';

import useAuth from 'hooks/useAuth';

// assets
import AuthBackground from './AuthBackground';

// ==============================|| AUTHENTICATION - WRAPPER ||============================== //

export default function AuthWrapper({ children }) {
  const { isLoggedIn } = useAuth();

  const [searchParams] = useSearchParams();
  const authParam = searchParams.get('auth') || '';

  return (
    <Box sx={{ minHeight: '100vh' }}>
      <AuthBackground />
      <Grid container direction="column" justifyContent="flex-end" sx={{ minHeight: '100vh' }}>
        <Grid sx={{ px: 3, mt: 3 }} size={12}>
          <Logo to="/" />
        </Grid>
        <Grid size={12}>
          <Grid
            container
            justifyContent="center"
            alignItems="center"
            sx={{ minHeight: { xs: 'calc(100vh - 210px)', sm: 'calc(100vh - 134px)', md: 'calc(100vh - 132px)' } }}
          >
            <Grid>
              <AuthCard>{children}</AuthCard>
              {!isLoggedIn && (
                <Box sx={{ maxWidth: { xs: 400, sm: 475 }, margin: { xs: 2.5, md: 3 }, '& > *': { flexGrow: 1, flexBasis: '50%' } }}>
                  <Grid size={12}>
                    <Divider sx={{ mb: 3 }}>
                      <Typography variant="caption"> OR </Typography>
                    </Divider>
                  </Grid>
                  <Grid size={12}>
                    <LoginProvider currentLoginWith={authParam} />
                  </Grid>
                </Box>
              )}
            </Grid>
          </Grid>
        </Grid>
        <Grid sx={{ p: 3 }} size={12}>
          <AuthFooter />
        </Grid>
      </Grid>
    </Box>
  );
}

AuthWrapper.propTypes = { children: PropTypes.node };
