import React from "react";
import Navbar from "./Navbar";
import ChatbaseBot from "./ChatbaseBot";

const Layout = ({ children }) => {
  return (
    <>
      <Navbar />
      <main>{children}</main>
      <ChatbaseBot /> {/* This makes it global across all pages */}
    </>
  );
};

export default Layout;
