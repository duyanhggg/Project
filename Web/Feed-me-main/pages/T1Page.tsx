import React, { useState } from 'react';
import '../styles/t1page.css';

const T1Page: React.FC = () => {
  const [selectedTab, setSelectedTab] = useState('overview');

  return (
    <div className="t1-page">
      {/* Header with sad emoji */}
      <div className="header-section">
        <div className="emoji-container">
          <div className="sad-emoji">😢</div>
        </div>
        <h1>NGƯỜI TÔI ĐỀ!</h1>
        <p className="subtitle">Về 5 Anh Hề</p>
      </div>

      {/* T1 - 5 ANH HỀ HUYỀN THOẠI */}
      <div className="content-section">
        <h2 className="section-title">
          <span className="badge">📍</span>
          <span className="badge">👱</span>
          T1 - 5 ANH HỀ HUYỀN THOẠI
        </h2>

        <div className="gallery-grid">
          <div className="gallery-item">
            <img src="https://via.placeholder.com/200x150?text=T1+Team+2025" alt="T1 Team 2025" />
            <p>T1 Team 2025</p>
          </div>
          <div className="gallery-item">
            <img src="https://via.placeholder.com/200x150?text=Faker+-+GOAT" alt="Faker - GOAT" />
            <p>Faker - GOAT</p>
          </div>
          <div className="gallery-item">
            <img src="https://via.placeholder.com/200x150?text=T1+at+Worlds" alt="T1 at Worlds" />
            <p>T1 at Worlds</p>
          </div>
          <div className="gallery-item">
            <img src="https://via.placeholder.com/200x150?text=T1+Coming+to+Vietnam" alt="T1 Coming to Vietnam" />
            <p>T1 Coming to Vietnam</p>
          </div>
        </div>

        <div className="alert-banner">
          <span className="alert-icon">📍</span>
          <p>Đây là lý do tôi cần cúc dưỡng cuối T1 đến Việt Nam là cơ hội của chúng tôi. Giúp tôi được 5 anh hề này! 🙏</p>
        </div>
      </div>

      {/* TẠI SAO NÊN NUÔI TÔI */}
      <div className="content-section">
        <h2 className="section-title">
          <span className="heart-icon">💖</span>
          TẠI SAO NÊN NUÔI TÔI?
        </h2>

        <div className="features-grid">
          <div className="feature-card">
            <div className="feature-icon">📈</div>
            <h3>Sao Kề Realtime</h3>
            <p>Cập nhật tứng giây! Nhằm hơn cả tác độ bạn chuyển tiền.</p>
          </div>

          <div className="feature-card">
            <div className="feature-icon">🔍</div>
            <h3>Mình Bạch 300%</h3>
            <p>Báo cáo có việc mua ủy trả số full topping.</p>
          </div>

          <div className="feature-card">
            <div className="feature-icon">🐷</div>
            <h3>Chỉ Tiêu Hợp Lý</h3>
            <p>Không G63. Chỉ mỡ 2 trăng và trà đá.</p>
          </div>

          <div className="feature-card">
            <div className="feature-icon">📱</div>
            <h3>App Tracking</h3>
            <p>Theo dõi 24/7 tôi anh, 📍 đâu như 'Big Brother'.</p>
          </div>
        </div>
      </div>

      {/* CAM KẾT VÀNG */}
      <div className="content-section">
        <h2 className="section-title">
          <span className="lock-icon">🔐</span>
          CAM KẾT VÀNG
        </h2>

        <div className="commitments-list">
          <div className="commitment-item">
            <span className="sun-icon">☀️</span>
            <p><strong>Sao kề mỗi ngày:</strong> Cập nhật tức cách sáng, đều như vật chanh!</p>
          </div>

          <div className="commitment-item">
            <span className="file-icon">📋</span>
            <p><strong>Không giấu giếm:</strong> Từ tô phó 50k đến hộp súa chưa 5k.</p>
          </div>

          <div className="commitment-item">
            <span className="money-icon">💰</span>
            <p><strong>Full hóa đơn:</strong> Chup bill, quét mã vạch, lưu biến lại đầy đủ.</p>
          </div>

          <div className="commitment-item">
            <span className="video-icon">📹</span>
            <p><strong>Video unboxing:</strong> Mở túng gì mì tôm live trên Facebook.</p>
          </div>

          <div className="commitment-item">
            <span className="phone-icon">📞</span>
            <p><strong>Hotline 24/7:</strong> Gọi hỏi tin anh gì bất cứ lúc nào.</p>
          </div>

          <div className="commitment-item">
            <span className="no-block-icon">🚫</span>
            <p><strong>Không block:</strong> Hội khó đến mây cùng trả lời.</p>
          </div>
        </div>
      </div>

      {/* SO SÁNH NÊ */}
      <div className="content-section comparison-section">
        <h2 className="section-title">
          <span className="compare-icon">⚖️</span>
          SO SÁNH NÊ
        </h2>

        <div className="comparison-cards">
          <div className="comparison-card bad">
            <h3>NGƯỜI KHÁC</h3>
            <ul>
              <li>❌ Sao kề sau 3 năm</li>
              <li>❌ File Excel mối tít</li>
              <li>❌ Số liệu "lầm tròn"</li>
              <li>❌ Hay block người hỏi</li>
            </ul>
          </div>

          <div className="comparison-card good">
            <h3>NGƯỜI TÔI</h3>
            <ul>
              <li>✅ Sao kề TRƯỚC khi tiêu</li>
              <li>✅ File Excel 4K Ultra HD</li>
              <li>✅ Chính xác từng đồng</li>
              <li>✅ Rep inbox siêu tốc</li>
            </ul>
          </div>
        </div>
      </div>

      {/* TIỀN BAY ĐI ĐẤU */}
      <div className="content-section">
        <h2 className="section-title">
          <span className="rocket-icon">🚀</span>
          TIỀN BAY ĐI ĐẤU?
        </h2>

        <div className="progress-section">
          <div className="progress-item">
            <label>Ăn uống</label>
            <div className="progress-bar">
              <div className="progress-fill" style={{ width: '10%', backgroundColor: '#FF6B6B' }}></div>
            </div>
            <span>10%</span>
          </div>

          <div className="progress-item">
            <label>Mua về</label>
            <div className="progress-bar">
              <div className="progress-fill" style={{ width: '60%', backgroundColor: '#4ECDC4' }}></div>
            </div>
            <span>60%</span>
          </div>

          <div className="progress-item">
            <label>Đi lại</label>
            <div className="progress-bar">
              <div className="progress-fill" style={{ width: '15%', backgroundColor: '#FFE66D' }}></div>
            </div>
            <span>15%</span>
          </div>

          <div className="progress-item">
            <label>Quà Cho Các Mom</label>
            <div className="progress-bar">
              <div className="progress-fill" style={{ width: '15%', backgroundColor: '#95E1D3' }}></div>
            </div>
            <span>15%</span>
          </div>

          <p className="progress-note">*Biểu đồ cấp nhật hàng tuần (nửa đầu dự!)</p>
        </div>
      </div>

      {/* DONATE SECTION */}
      <div className="donate-section">
        <div className="donate-content">
          <h2>💳 DONATE NGAY ĐI!</h2>
          <p>(Nếu bạn đã cuối khi độc nhìng động trên)</p>

          <div className="qr-code">
            <img src="https://via.placeholder.com/150x150?text=QR+CODE" alt="QR Code for donation" />
          </div>

          <p className="donation-note">Chuyển song là tài mail tự dùng</p>

          <div className="payment-methods">
            <div className="payment-item">
              <span className="bank-icon">🏦</span>
              <div className="payment-text">
                <label>MB</label>
                <input type="text" value="10491922182007" readOnly />
              </div>
              <button className="copy-btn">📋</button>
            </div>

            <div className="payment-item">
              <span className="payment-icon">📱</span>
              <div className="payment-text">
                <label>Momo</label>
                <input type="text" value="0909 999 888" readOnly />
              </div>
              <button className="copy-btn">📋</button>
            </div>
          </div>
        </div>
      </div>

      {/* DISCLAIMER */}
      <div className="disclaimer">
        <p>⚠️ DISCLAIMER: Đây là trang web minh chứng chính chủ HẦM HƯỚC. Mục nội dung đếu này giải tiếp chức chúc mục.</p>
      </div>
    </div>
  );
};

export default T1Page;
