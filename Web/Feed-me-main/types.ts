export interface UserProfile {
  name: string;
  email: string; // Used as identifier
  avatarUrl: string;
  slogan: string;
  bankName: string;
  bankAccount: string;
  walletName: string;
  walletAccount: string;
  qrCodeUrl: string;
  title: string;
  description: string;
  goal: number;
  currency: string;
  story: string;
  // Có thể thêm:
  eventDate?: string; // Ngày sự kiện T1
  location?: string; // Địa điểm sự kiện
}

export const DEFAULT_PROFILE: UserProfile = {
  name: "BẠN TỐT BỤNG",
  email: "",
  avatarUrl: "https://api.dicebear.com/7.x/fun-emoji/svg?seed=Lucky",
  slogan: "\"Sự giàu có của tôi phụ thuộc vào lòng tốt của bạn\"",
  bankName: "Techcombank",
  bankAccount: "1900 1234 5678",
  walletName: "Momo",
  walletAccount: "0909 999 888",
  qrCodeUrl: "https://api.qrserver.com/v1/create-qr-code/?size=150x150&data=ThankYou",
  title: "",
  description: "",
  goal: 0,
  currency: "",
  story: "",
};