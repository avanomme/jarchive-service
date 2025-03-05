class ApiKey < ApplicationRecord
  validates :name, presence: true
  validates :key, presence: true, uniqueness: true
  validates :active, inclusion: { in: [true, false] }
  
  before_validation :generate_key, on: :create
  
  private
  
  def generate_key
    self.key = SecureRandom.hex(32)
  end
end 