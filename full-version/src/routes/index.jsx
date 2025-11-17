import { lazy } from 'react';
import { createBrowserRouter, Navigate } from 'react-router-dom';

// project imports
import MainRoutes from './MainRoutes';
import LoginRoutes from './LoginRoutes';
import ComponentsRoutes from './ComponentsRoutes';

import { APP_DEFAULT_PATH } from 'config';
import { SimpleLayoutType } from 'config';
import SimpleLayout from 'layout/Simple';
import Loadable from 'components/Loadable';
import useAuth from 'hooks/useAuth';

// render - landing page
const PagesLanding = Loadable(lazy(() => import('pages/landing')));

// root redirect component
const RootRedirect = () => {
  const { isLoggedIn } = useAuth();

  if (isLoggedIn) {
    return <Navigate to={APP_DEFAULT_PATH} replace />;
  }

  return <Navigate to="/login" replace />;
};

// ==============================|| ROUTING RENDER ||============================== //

const router = createBrowserRouter(
  [
    {
      path: '/',
      element: <RootRedirect />
    },
    {
      path: '/landing',
      element: <SimpleLayout layout={SimpleLayoutType.LANDING} />,
      children: [
        {
          index: true,
          element: <PagesLanding />
        }
      ]
    },
    LoginRoutes,
    ComponentsRoutes,
    MainRoutes
  ],
  { basename: import.meta.env.VITE_APP_BASE_NAME }
);

export default router;
