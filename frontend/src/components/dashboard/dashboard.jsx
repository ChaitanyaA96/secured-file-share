import React, { useState, useEffect } from 'react';
import { useDispatch, useSelector } from 'react-redux';
import { Layout, Menu, Avatar, Spin } from 'antd';
import { FileOutlined, UserOutlined } from '@ant-design/icons';
import MyFiles from './myfiles';
import SharedWithMe from './sharedWithMe';
import FileShareModal from './fileshare';
import { loadUser } from '../../actions/auth';
import { loadMyFiles, loadSharedWithMe } from '../../actions/file';
import { useNavigate } from 'react-router-dom';
const { Sider, Header, Content } = Layout;

function Dashboard() {
  const [collapsed, setCollapsed] = useState(false);
  const [activeMenu, setActiveMenu] = useState('my-files'); // Track active menu
  const user = useSelector((state) => state.auth.user);
  const dispatch = useDispatch();

  const { myFiles, sharedFiles, loading } = useSelector((state) => ({
    myFiles: state.file.myFiles,
    sharedFiles: state.file.sharedWithMe,
    loading: state.file.loading, // Add loading state in your reducer if not already present
  }));

  // Load user and files on mount
  useEffect(() => {
    dispatch(loadUser());
    if (activeMenu === 'my-files') {
      dispatch(loadMyFiles());
    } else if (activeMenu === 'shared-with-me') {
      dispatch(loadSharedWithMe());
    }
  }, [dispatch, activeMenu]); // Reload files when activeMenu changes

  const handleMenuClick = ({ key }) => {
    setActiveMenu(key); // Set the active menu
  };

  return (
    <Layout style={{ minHeight: '100vh' }}>
      <Sider collapsible collapsed={collapsed} onCollapse={(value) => setCollapsed(value)}>
        <div style={{ margin: '16px', textAlign: 'center' }}>
          <Avatar size={64} icon={<UserOutlined />} />
          {!collapsed && (
            <div>
              <p>{user.first_name} {user.last_name}</p>
              <p>{user.email}</p>
            </div>
          )}
        </div>
        <Menu
          theme="dark"
          mode="inline"
          defaultSelectedKeys={['my-files']}
          onClick={handleMenuClick}
          items={[
            {
              key: 'user-page',
              icon: <UserOutlined />,
              label: 'User Page',
            },
            {
              key: 'my-files',
              icon: <FileOutlined />,
              label: 'My Files',
            },
            {
              key: 'shared-with-me',
              icon: <FileOutlined />,
              label: 'Shared With Me',
            },
          ]}
        />
      </Sider>

      <Layout>
        <Header style={{ background: '#fff', padding: 0 }} />
        <Content style={{ margin: '16px' }}>
          {loading ? (
            <Spin size="large" style={{ display: 'block', margin: '50px auto' }} />
          ) : (
            <>
              {activeMenu === 'my-files' && <MyFiles files={myFiles} />}
              {activeMenu === 'shared-with-me' && <SharedWithMe files={sharedFiles} />}
              {activeMenu === 'user-page' && <div>User Page Placeholder</div>}
              <FileShareModal />
            </>
          )}
        </Content>
      </Layout>
    </Layout>
  );
}

export default Dashboard;
