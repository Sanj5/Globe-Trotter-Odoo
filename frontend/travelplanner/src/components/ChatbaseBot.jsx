import { useState } from "react";
import "./ChatbaseBot.css"; // ✅ Match the filename correctly

const ChatbaseBot = () => {
  const [isOpen, setIsOpen] = useState(false);

  const toggleBot = () => {
    setIsOpen(!isOpen);
  };

  return (
    <div className="chatbot-container">
      {/* Floating Chat Icon */}
      <button className="chatbot-icon" onClick={toggleBot}>
        💬
      </button>

      {/* Chat Popup Window */}
      {isOpen && (
        <div className="chatbot-popup">
          <div className="chatbot-header">
            <span>Need Help?</span>
            <button className="close-btn" onClick={toggleBot}>
              ✖
            </button>
          </div>
          <iframe
            src="https://www.chatbase.co/chatbot-iframe/l502MYOHFq__2MLX4th5B"
            title="ChatbaseBot"
            width="100%"
            height="100%"
            style={{ border: "none", borderRadius: "10px" }}
          ></iframe>
        </div>
      )}
    </div>
  );
};

export default ChatbaseBot;
