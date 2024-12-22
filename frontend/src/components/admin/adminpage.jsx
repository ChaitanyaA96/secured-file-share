// import React from 'react';
// import { Typography } from 'antd';

// const { Title, Paragraph } = Typography;

// const AdminPage = () => {
//   return (
//     <div>
//       <Title level={2}>Admin Dashboard</Title>
//       <Paragraph>
//         This area provides administration functionalities such as managing users, setting roles, and more.
//       </Paragraph>
//     </div>
//   );
// };

// export default AdminPage;


import React from 'react';
import { Layout, Menu } from 'antd';
import {
  UserOutlined,
  FileOutlined,
} from '@ant-design/icons';
import { Routes, Route, Link } from 'react-router-dom';
import User from './user';
import File from './file';

const { Header, Content, Sider } = Layout;

const AdminPage = () => {
  return (
    <Layout>
      <Header className="header">
        <div className="logo" />
        <Menu theme="dark" mode="horizontal">
          <Menu.Item key="1">Admin Dashboard</Menu.Item>
        </Menu>
      </Header>
      <Layout>
        <Sider width={200} className="site-layout-background">
          <Menu
            mode="inline"
            defaultSelectedKeys={['1']}
            style={{ height: '100%', borderRight: 0 }}
          >
            <Menu.Item key="1" icon={<UserOutlined />}>
              <Link to="/admin/users">Users</Link>
            </Menu.Item>
            <Menu.Item key="2" icon={<FileOutlined />}>
              <Link to="/admin/files">Files</Link>
            </Menu.Item>
          </Menu>
        </Sider>
        <Layout style={{ padding: '24px' }}>
          <Content
            className="site-layout-background"
            style={{
              padding: 24,
              margin: 0,
              minHeight: 280,
            }}
          >
            <Routes>
              <Route path="/users" element={<User />} />
              <Route path="/files" element={<File />} />
            </Routes>
          </Content>
        </Layout>
      </Layout>
    </Layout>
  );
};

export default AdminPage;
