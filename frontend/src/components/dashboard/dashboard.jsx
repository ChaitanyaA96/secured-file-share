import React, { useState, useEffect, useMemo } from 'react'
import { useDispatch, useSelector } from 'react-redux'
import { Layout, Menu, Avatar, Spin } from 'antd'
import { FileOutlined, UserOutlined } from '@ant-design/icons'
import MyFiles from './myfiles'
import SharedWithMe from './sharedWithMe'
import FileShareModal from './fileshare'
import { loadUser } from '../../actions/auth'
import { loadMyFiles, loadSharedWithMe } from '../../actions/file'

const { Sider, Header, Content } = Layout

function Dashboard() {
  const [collapsed, setCollapsed] = useState(false)
  const [activeMenu, setActiveMenu] = useState('my-files') // Track active menu
  const dispatch = useDispatch()

  // Use selector to get user data
  const user = useSelector((state) => state.auth.user)

  // Use selector for file state and memoize derived data
  const fileState = useSelector((state) => state.file)
  const { myFiles, sharedFiles, loading } = useMemo(() => {
    return {
      myFiles: fileState.myFiles || [],
      sharedFiles: fileState.sharedWithMe || [],
      loading: fileState.loading || false,
    }
  }, [fileState])

  // Load user and files on mount or when the active menu changes
  useEffect(() => {
    dispatch(loadUser())
    if (activeMenu === 'my-files') {
      dispatch(loadMyFiles())
    } else if (activeMenu === 'shared-with-me') {
      dispatch(loadSharedWithMe())
    }
  }, [dispatch, activeMenu])

  // Handle menu selection
  const handleMenuClick = ({ key }) => {
    setActiveMenu(key) // Update active menu
  }

  return (
    <Layout style={{ minHeight: '100vh' }}>
      <Sider
        collapsible
        collapsed={collapsed}
        onCollapse={(value) => setCollapsed(value)}
      >
        <div style={{ margin: '16px', textAlign: 'center' }}>
          <Avatar size={64} icon={<UserOutlined />} />
          {!collapsed && (
            <div>
              <p>
                {user?.first_name || 'User'} {user?.last_name || ''}
              </p>
              <p>{user?.email || 'user@example.com'}</p>
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
            <Spin
              size="large"
              style={{ display: 'block', margin: '50px auto' }}
            />
          ) : (
            <>
              {activeMenu === 'my-files' && <MyFiles files={myFiles} />}
              {activeMenu === 'shared-with-me' && (
                <SharedWithMe files={sharedFiles} />
              )}
              {activeMenu === 'user-page' && <div>User Page Placeholder</div>}
              <FileShareModal />
            </>
          )}
        </Content>
      </Layout>
    </Layout>
  )
}

export default Dashboard
