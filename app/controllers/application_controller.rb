class ApplicationController < ActionController::Base
  protect_from_forgery

  after_action :set_access_control_headers

  def set_access_control_headers
    headers['Access-Control-Allow-Origin'] = "*"
    headers['Access-Control-Request-Method'] = %w{GET POST OPTIONS}.join(",")
  end

  private

  def authenticate_api_key
    api_key = request.headers['X-API-Key']
    @current_api_key = ApiKey.find_by(key: api_key, active: true)
    
    unless @current_api_key
      render json: { error: 'Invalid or inactive API key' }, status: :unauthorized
    end
  end
end
